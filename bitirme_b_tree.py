import bitirme_database as db


def sort_for_all_dimension(env, record_num, dimension, mcr_type):
    index_file = 'bitirme_index.db'
    
    
    record_list_sorted_for_all_dims = dimension*[None]
    records = db.select_all(env)
    records_dict = {record["record_id"]: record for record in records}
    all_record_ids = list(records_dict.keys())
    
    for d in range(1, dimension + 1):
        record_list_sorted = sorted(all_record_ids, 
                                key=lambda x: records_dict[x]['var_'+str(d)],
                                    reverse=bool(mcr_type))   
               
        record_list_sorted_for_all_dims[d - 1] = record_list_sorted
        
        
    counter = (record_num + 1) * [0]    
    breakable = 0
    
    for r in range(record_num):
        
        if breakable == 1:
            break
          
        for d in range(dimension):
            record_id = record_list_sorted_for_all_dims[d][r]
            record_id = int(record_id[7:])
            counter[record_id] +=1
            
            if(counter[record_id] == dimension):
                breakable = 1
                break


    b_tree_record_list = []   
    
    for r in range(1, record_num + 1):
        if counter [r] != 0:
            b_tree_record_list.append(records_dict['record_' + str(r)])
    
    
    index_env = db.create_index_file(index_file, b_tree_record_list, dimension)
       
    return index_env

