import json
import os
import time
import bitirme_record_comparison as rec_comp

def iterate_bnl(temp_file_order, dimension, mcr_type,
                window, window_size):

    for i in range(len(window)) :
        window[i]['flag'] = True
    
    is_file_empty = True
    comparation_count = 0
    compare_records = rec_comp.compare_records
    
    if(temp_file_order % 2 == 0):
        temp_file_in  = 'temp_file_1.json'
        temp_file_out = 'temp_file_2.json'
    else:
        temp_file_in  = 'temp_file_2.json'
        temp_file_out = 'temp_file_1.json'
    
    
    
    with open(temp_file_in, "r") as f_in, open(temp_file_out, "w") as f_out :
        
        for line in f_in:
            if not line.strip(): continue   
            
            record = json.loads(line)
            append_record = True
    
            for w in range(len(window)):
                comparation_count += 1
                result = compare_records(record, window[w],
                                                  dimension, mcr_type)

                
                if result == 1:
                    # record window[w]'i domine ediyor → window[w] boşalt
                    window[w] = None

                elif result == 2:
                    # window[w] record'u domine ediyor → record eklenmeyecek
                    append_record = False

            window = [wi for wi in window if wi != None]

            if append_record == 1 :  
                if len(window) < window_size :
                    if is_file_empty :
                        record['flag'] = True
                    else :
                        record['flag'] = False
                    window.append(record)
                       
                else:
                    is_file_empty = False
                    f_out.write(json.dumps(record) + "\n")
         
            
    if is_file_empty :
        os.remove(temp_file_in)
        os.remove(temp_file_out)

    return window, is_file_empty, comparation_count
    
    

def block_nested_loop(env, dimension, mcr_type, window_size):
    
    undominated_records = []
    window = []
    compare_records = rec_comp.compare_records
    
    is_file_empty = True
    temp_file_order = 0
    is_skyline_empty = True
    comparation_count = 0
    start = time.perf_counter()
    
    with env.begin() as txn, open('temp_file_1.json', "w") as temp_file:
        cursor = txn.cursor()
       
        for key, value in cursor:
            append_record = 1
            record = json.loads(value.decode())
 
   
            for w in range(len(window)) :
                comparation_count += 1
                comparation_result = compare_records(record,window[w],
                                                     dimension, mcr_type)
                if comparation_result == 1 :
                    window[w] = None
                   
                if comparation_result == 2 :
                    append_record = 0
   
            window = [wi for wi in window if wi != None]
   
            if append_record == 1 :  
                if len(window) < window_size :
                    if is_file_empty :
                        record['flag'] = True
                    else :
                        record['flag'] = False
                    window.append(record)
                                 
                else:
                    is_file_empty = False
                    temp_file.write(json.dumps(record) + "\n")

    for i in range(len(window)) :
        if window[i]['flag'] == True :
            if is_skyline_empty:
                is_skyline_empty = False
                response_time = time.perf_counter() - start
            undominated_records.append(window[i]['record_id'])
            window[i] = None
    window = [w for w in window if w is not None]
   
   
       
    while is_file_empty == False :
        window, is_file_empty, new_comp =iterate_bnl(temp_file_order, dimension,
                                            mcr_type, window, window_size)
        comparation_count += new_comp
        
        for i in range(len(window)) :
            if window[i]['flag'] == True :
                if is_skyline_empty:
                    is_skyline_empty = False
                    response_time = time.perf_counter() - start
                undominated_records.append(window[i]['record_id'])
                window[i] = None
        window = [w for w in window if w is not None]
        temp_file_order += 1 
        
    undominated_records += [item['record_id'] for item in window]
    #print('Json dosyası silindi.')
   
    undominated_records = [x for x in undominated_records if x is not None]
       
    return undominated_records, response_time, comparation_count