import bitirme_database as db
import bitirme_record_comparison as rec_comp

def merge_step(left_skyline, right_skyline, dimension, mcr_type, counter):
    # Sağdakiler tarafından domine edilen sol elemanları takip etmek için bir set
    dominated_left_indices = set()
    final_right = []
    
    for r_right in right_skyline:
        is_dominated_by_left = False
        
        for i, r_left in enumerate(left_skyline):
            counter[0] += 1
            result = rec_comp.compare_records(r_left, r_right, dimension, mcr_type)
            
            if result == 1: # Sol, sağdaki elemanı (r_right) eziyor
                is_dominated_by_left = True
                break
            elif result == 2: # Sağ, soldaki elemanı (r_left) eziyor
                dominated_left_indices.add(i)
        
        if not is_dominated_by_left:
            final_right.append(r_right)
            
    # Sadece domine edilmemiş sol elemanları filtrele
    final_left = [el for i, el in enumerate(left_skyline) if i not in dominated_left_indices]
    
    # İki listeyi birleştir
    return final_left + final_right

def dnc_recursive_multidim(records, total_dims, current_dim, mcr_type, counter):
    n = len(records)
    
    # Base Case: Tek eleman kaldıysa döndür
    if n <= 1:
        return records
    
    # 1. ADIM: Şu anki boyuta (current_dim) göre SIRALA
    # Senin istediğin mantık burada: Her derinlikte liste tekrar sıralanıyor.
    is_reverse = True if mcr_type == 1 else False
    
    # Not: Python'un Timsort'u çok hızlıdır, bu işlem güvenlidir.
    records.sort(key=lambda x: x['var_' + str(current_dim)], reverse=is_reverse)
    
    # 2. ADIM: Böl (Divide)
    mid = n // 2
    left_part = records[:mid]
    right_part = records[mid:]
    
    # 3. ADIM: Bir sonraki boyut indeksini belirle (1 -> 2 -> ... -> 10 -> 1)
    # Modulo işlemi ile döngüsel yapıyoruz.
    next_dim = (current_dim % total_dims) + 1
    
    # 4. ADIM: Özyineleme (Recursion) - Yeni boyutla çağır
    s1 = dnc_recursive_multidim(left_part, total_dims, next_dim, mcr_type, counter)
    s2 = dnc_recursive_multidim(right_part, total_dims, next_dim, mcr_type, counter)
    
    # 5. ADIM: Birleştir (Merge)
    return merge_step(s1, s2, total_dims, mcr_type, counter)

def divide_and_conquer(env, dimension, mcr_type):
    # Veriyi çek
    record_list = db.select_all(env)
    counter = [0]
    # Algoritmayı 1. boyuttan başlayarak çağır
    skyline_records = dnc_recursive_multidim(record_list, dimension, 
                                             1, mcr_type, counter)
    
    # ID listesi döndür
    return [rec['record_id'] for rec in skyline_records], counter[0]