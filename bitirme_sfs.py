import time
import bitirme_database as db
import bitirme_record_comparison as rec_comp


def dist_from_zero_point(record, dimension):
    dist = 0
    for d in range(1, dimension + 1):
        dist += record['var_' + str(d)]**2
    return dist


def sort_filter_skyline(env, dimension, mcr_type):
    records = db.select_all(env)
    skyline = []
    skyline_len = 1
    record_num = len(records)
    
    comparison_count = 0
    response_time = 0

    compare_records = rec_comp.compare_records
    start = time.perf_counter()
    
    for i in range(record_num):
        distance = dist_from_zero_point(records[i], dimension) 
        records[i]['dist'] = distance
        
    records.sort(key=lambda x: x['dist'], reverse = mcr_type)
    skyline.append(records[0])
    response_time = time.perf_counter() - start
    
    for i in range(1, record_num):
        is_dominated = False
        for j in range(skyline_len):
            comparison_count += 1
            result = compare_records(records[i], skyline[j], 
                                              dimension, mcr_type)
            if result == 2:
                is_dominated = True
                break
            
        if is_dominated == False :
            skyline_len += 1
            skyline.append(records[i])
            
    skyline = [s['record_id'] for s in skyline]
    
    return skyline, response_time, comparison_count