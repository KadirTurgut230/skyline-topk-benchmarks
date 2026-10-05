import time
from collections import Counter
import tracemalloc

import bitirme_database as db
import bitirme_plotter as plt
import bitirme_nnl as nnl
import bitirme_bnl as bnl
import bitirme_dc as dc
import bitirme_sfs as sfs
import bitirme_b_tree as b_tree
import bitirme_bbs as bbs

def single_skyline_algorithm(item_list, mcr_type, value_limit, 
                            selected_algorithm):
    
    db_name = 'records_db'
    window_size = 20
    capacity = 20
    selected_measurement = [1, 2, 3, 4]
    
    skyline = []
    records = []
    data_matrix = []
    #env = db.create_db(db_name, 5, 5, value_limit)
    
    execution_type = 1
    
    
    for item in item_list:
        new_list = []
        skyline_item = []
        if execution_type == 1:
            #db.drop_db(db_name, env) 
            record_num = item[0]
            dimension = item[1]
            env = db.create_db(db_name, record_num, dimension, value_limit)
            records.append(db.select_all(env))
        
        if 1 in selected_measurement :
            start = time.time()
        if 2 in selected_measurement :
            tracemalloc.start()
            
        if execution_type == 1:
            
            if selected_algorithm == 1:
                skyline_item, response_time,comp_count = nnl.naive_nested_loop(env,
                                                    record_num, dimension, mcr_type)
            elif selected_algorithm == 2:
                skyline_item, response_time, comp_count= bnl.block_nested_loop(env, 
                                                dimension, mcr_type, window_size)
            elif selected_algorithm == 3:  
                skyline_item, comp_count=dc.divide_and_conquer(env, dimension, 
                                                              mcr_type)
                response_time = time.time() - start
            elif selected_algorithm == 4:
                skyline_item, response_time,comp_count =sfs.sort_filter_skyline(env,
                                                dimension, mcr_type)
            elif selected_algorithm == 5:
                index_file = b_tree.sort_for_all_dimension(env, 
                                                record_num, dimension, mcr_type)
                response_time_1 = time.time() - start
                skyline_item, response_time,comp_count =sfs.sort_filter_skyline(
                                    index_file, dimension, mcr_type)
                response_time += response_time_1 
                db.drop_db('bitirme_index.db', index_file)
                
            elif selected_algorithm == 6:
                skyline_item, response_time, comp_count =  bbs.bbs_algorithm(env,
                                                    dimension,mcr_type, capacity)
                    
        skyline.append(skyline_item)
        
        if 1 in selected_measurement :
            end = time.time()
            overall_time = round(end - start , 2)
            new_list.append(overall_time)
            #print(i, ' için Geçen Zaman : ', end - start )
        if 2 in selected_measurement :
            current, peak = tracemalloc.get_traced_memory()
            #print(i, f" Anlık kullanım: {current / 10**6:.2f} MB")
            #print(i, f" En yüksek (peak) kullanım: {peak / 10**6:.2f} MB")
            tracemalloc.stop()
            new_list.append(round(peak / 10**6, 2))
        if 3 in selected_measurement :
            new_list.append(round(response_time, 2))
            #print(i, ' için Response Time : ', response_time )
        if 4 in selected_measurement :
            new_list.append(int(comp_count))
    
        db.drop_db(db_name, env)
        data_matrix.append(new_list)
         
        
    data_matrix = list(map(list, zip(*data_matrix)))  
    
    
    x_data = [] 
    x = []
    for item in item_list:
        if execution_type == 1:
            string = f'Dataset Volume : {item[0]} Dimension : {item[1]}'
            x_data.append(string)
            string = str(item[0]) + ' - ' + str(item[1])
            x.append(string)
        elif execution_type == 2:
            x_data.append('Window Size : ' + str(item))
        elif execution_type == 3:
            x_data.append('Capacity : ' + str(item))
        
        
        
    selected_measurement_str = []   
    if 1 in selected_measurement:
        selected_measurement_str.append('Overall Time(second)')
    if 2 in selected_measurement:
        selected_measurement_str.append('Ram Usage(MB)')
    if 3 in selected_measurement:
        selected_measurement_str.append('Response Time(second)')    
    if 4 in selected_measurement:
        selected_measurement_str.append('Number of Record Comparison')      
    
    title = ''
    x_label = ''
    if execution_type == 1 :
        x_label = 'Dataset Volume - Dimension'
        if selected_algorithm ==   1:
           title = 'NNL'
        elif selected_algorithm == 2:
           title = 'BNL'  
        elif selected_algorithm == 3:
           title = 'Divide and Conquer'   
        elif selected_algorithm == 4:
           title = 'SFS' 
        elif selected_algorithm == 5:
           title = 'B - Tree'
        elif selected_algorithm == 6:
           title = 'R - Tree (BBS)' 
           
    fig_list = []      
    fig = plt.create_matrix_table(x_data, selected_measurement_str, 
                            data_matrix, title)
    fig_list.append(fig)
    
    
    for i in range(len(selected_measurement)):
        y = data_matrix[i]
        y_label = selected_measurement_str[i]
        #x_label = 'Number of Records, Dimension'
        fig = plt.create_plot(x, y, y_label, title, x_label)
        fig_list.append(fig)

    return records, skyline, fig_list

"""
item_list = [[10, 2],[15, 2]]
selected_algorithm = 4
value_limit = [5, 100, 10, 30, 50, 20, 50, 90, 100, 120]
mcr_type = 0

records, skyline, fig_list = single_skyline_alorithm(item_list, mcr_type, 
                                        value_limit, selected_algorithm)
print(records)
print(skyline)
"""