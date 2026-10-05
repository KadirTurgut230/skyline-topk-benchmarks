import time
import bitirme_database as db
import bitirme_record_comparison as rec_comp

def naive_nested_loop(env, record_num, dimension, mcr_type):
    records = db.select_all(env)
    skyline = []
    
    comparison_count = 0
    response_time = 0
    is_skyline_empty = True
    
    compare_records = rec_comp.compare_records
    
    start = time.perf_counter()
    for record_1 in records:
        is_dominated = False
        
        for record_2 in records:
            comparison_count += 1
            comparation_result = compare_records(record_1, record_2, 
                                                         dimension, mcr_type)
                
            if comparation_result == 2:
                is_dominated = True
                break
            
        if is_dominated == False :
            if is_skyline_empty:
                is_skyline_empty = False
                response_time = time.perf_counter() - start
            skyline.append(record_1['record_id'])
    
            
    return skyline, response_time, comparison_count 