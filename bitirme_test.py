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


def compare_algorithms(record_num, dimension, mcr_type, value_limit, 
                       selected_algorithms):
    db_name = 'records_db'
    window_size = 20
    capacity = 20
    
    env = db.create_db(db_name, record_num, dimension, value_limit)
    
    #selected_algorithms = [1,2,3,4,5,6]
    selected_measurement = [1, 2, 3, 4]
    data_matrix = []
    
    skyline_list = []
    
    for i in range(1, 7) :
        if i in selected_algorithms :
            new_list = []
            if 1 in selected_measurement :
                start = time.time()
            if 2 in selected_measurement :
                tracemalloc.start()
                
                
            if i == 1:
                skyline, response_time, comp_count = nnl.naive_nested_loop(env,
                                                    record_num, dimension, mcr_type)
                skyline_list.append(skyline)
                
            elif i == 2:
                skyline, response_time, comp_count= bnl.block_nested_loop(env, 
                                                dimension, mcr_type, window_size)
                skyline_list.append(skyline)
                
            elif i == 3:
                skyline, comp_count=dc.divide_and_conquer(env, dimension, mcr_type)
                response_time = time.time() - start
                skyline_list.append(skyline)
                
            elif i == 4:
                skyline, response_time, comp_count = sfs.sort_filter_skyline(env,
                                                    dimension, mcr_type)
                skyline_list.append(skyline)
            elif i == 5:
                index_file = b_tree.sort_for_all_dimension(env, 
                                                record_num, dimension, mcr_type)
                response_time_1 = time.time() - start
                skyline, response_time, comp_count = sfs.sort_filter_skyline(
                                                index_file, dimension, mcr_type)
                response_time += response_time_1 
                db.drop_db('bitirme_index.db', index_file)
                skyline_list.append(skyline)
            elif i == 6:
                skyline, response_time, comp_count =  bbs.bbs_algorithm(env,
                                                    dimension,mcr_type, capacity)
                skyline_list.append(skyline)
                
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
                #print(i, ' için Comparison Count : ', comp_count )
           #print('\n\n')
            data_matrix.append(new_list)
    
    
    result_control = True
    base_skyline = skyline_list[0]
    for skyline in skyline_list :
        if not Counter(base_skyline) == Counter(skyline) :
            print('Hatalı Algo : ')
            result_control = False
            
    print(f'\nResult = {result_control} ')
    records = db.select_all(env)
    db.drop_db(db_name, env)        
            
            
    selected_algorithms_str = []
    selected_measurement_str = []    
            
    if 1 in selected_algorithms:
        selected_algorithms_str.append('NNL')
    if 2 in selected_algorithms:
        selected_algorithms_str.append('BNL')
    if 3 in selected_algorithms:
        selected_algorithms_str.append('Divide and Conquer')
    if 4 in selected_algorithms:
        selected_algorithms_str.append('SFS')
    if 5 in selected_algorithms:
        selected_algorithms_str.append('B - Tree')
    if 6 in selected_algorithms:
        selected_algorithms_str.append('R - Tree(BBS)')
    
    
    if 1 in selected_measurement:
        selected_measurement_str.append('Overall Time(second)')
    if 2 in selected_measurement:
        selected_measurement_str.append('Ram Usage(MB)')
    if 3 in selected_measurement:
        selected_measurement_str.append('Response Time(second)')    
    if 4 in selected_measurement:
        selected_measurement_str.append('Number of Record Comparison')    
            
           
    data_matrix = list(map(list, zip(*data_matrix)))
    title = 'Dataset Volume : ' + str(record_num)
    title += '  Dimension : ' + str(dimension)
    
    fig_list = []
    fig = plt.create_matrix_table(selected_algorithms_str, 
                                  selected_measurement_str, data_matrix, title)
    fig_list.append(fig)
    
    for i in range(len(selected_measurement)):
        x = selected_algorithms_str
        y = data_matrix[i]
        y_label = selected_measurement_str[i]
        fig = plt.create_plot(x, y, y_label, title)
        fig_list.append(fig)
   
    return records, skyline_list, result_control, fig_list


"""
record_num = 20
dimension = 2
mcr_type = 1
value_limit = [5, 100, 10, 30, 50, 20, 50, 90, 100, 120]
selected_algorithms = [1,2, 3,4,  5, 6]

records, skyline_list, result_control, fig_list= compare_algorithms(
                                record_num, dimension, mcr_type, value_limit, 
                                                        selected_algorithms)
print(records)
print(skyline_list)
"""