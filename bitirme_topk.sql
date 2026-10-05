-- =========================================================
-- 1. TABLO OLUŞTURUCU
-- =========================================================
CREATE OR REPLACE FUNCTION create_top_k_table(record_num integer, dimension integer, arr integer[])
RETURNS VOID AS $$
DECLARE
    i INTEGER; j INTEGER; var_name TEXT; 
    column_names TEXT := 'record_id'; value_list TEXT; random_value INTEGER;
BEGIN
    DROP TABLE IF EXISTS top_k_table CASCADE;
    CREATE TABLE top_k_table (record_id VARCHAR(20) PRIMARY KEY);
    
    FOR i IN 1 .. dimension LOOP
        var_name := 'var_' || i::TEXT;
        EXECUTE format('ALTER TABLE top_k_table ADD COLUMN %I INTEGER', var_name);
        column_names := column_names || ', ' || var_name;
    END LOOP;

    FOR j IN 1 .. record_num LOOP
        value_list := quote_literal('record_' || j::TEXT);
        FOR i IN 1 .. dimension LOOP
            random_value := floor(random() * (arr[i] + 1))::INTEGER;
            value_list := value_list || ', ' || random_value::TEXT;
        END LOOP;
        EXECUTE format('INSERT INTO top_k_table (%s) VALUES (%s)', column_names, value_list);
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- =========================================================
-- 2. NAIVE SORGULAMA (ROUNDING + DETERMINISTIC SORT)
-- =========================================================
CREATE OR REPLACE FUNCTION top_k_query(
    p_table_name TEXT,
    grades FLOAT[],
    k Integer, 
    mcr_type boolean
)
RETURNS TABLE (
    record_id TEXT,
    total_score NUMERIC
)
LANGUAGE plpgsql
AS $$
DECLARE
    col_record RECORD;
    score_expr TEXT := '';
    final_query TEXT;
    i INTEGER := 1;
BEGIN
    -- Sütunları gez ve Normalizasyon formülünü ekle
    FOR col_record IN
        SELECT c.column_name FROM information_schema.columns c
        WHERE c.table_name = p_table_name AND c.column_name LIKE 'var_%'
        ORDER BY c.ordinal_position
    LOOP
        IF i > array_length(grades, 1) THEN EXIT; END IF;
        
        -- Formül: w * (val - min) / (max - min)
        score_expr := score_expr || format(
            ' + COALESCE( (%s * (CAST(%I AS NUMERIC) - MIN(%I) OVER()) / ' ||
            ' NULLIF(MAX(%I) OVER() - MIN(%I) OVER(), 0)) , 0)',
            grades[i], col_record.column_name, col_record.column_name, 
            col_record.column_name, col_record.column_name
        );
        i := i + 1;
    END LOOP;
    
    IF score_expr = '' THEN score_expr := '0'; END IF;
    IF score_expr != '0' THEN score_expr := '0' || score_expr; END IF;

    -- ROUND(..., 5) -> Hassasiyet hatalarını engeller
    -- ORDER BY ..., record_id ASC -> Puan eşitse ID sırasına bakar
    final_query := format(
        'SELECT t.record_id::TEXT, ROUND((%s)::NUMERIC, 5) AS total_score FROM %I t ' ||
        'ORDER BY total_score %s, t.record_id ASC ' ||
        'LIMIT %s',
        score_expr,
        p_table_name,
        CASE WHEN mcr_type = TRUE THEN 'DESC' ELSE 'ASC' END,
        k
    );

    RETURN QUERY EXECUTE final_query;
END;
$$;