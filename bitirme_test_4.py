import bitirme_database as db
import bitirme_plotter as plt
import bitirme_nnl as nnl
import bitirme_bnl as bnl
import bitirme_dc as dc
import bitirme_sfs as sfs
import bitirme_b_tree as b_tree
import bitirme_bbs as bbs


db_name = 'records_db'
record_num = 100
dimension = 2
mcr_type = 1

value_limit = [20, 20]

window_size = 5
capacity = 5

env = db.create_db(db_name, record_num, dimension, value_limit)
records = db.select_all(env)
plt.plot_records(records)


skyline, response_time, comp_count = nnl.naive_nested_loop(env,
                                    record_num, dimension, mcr_type)
print('NNL: ', skyline)


skyline, response_time, comp_count= bnl.block_nested_loop(env, 
                                dimension, mcr_type, window_size)
print('BNL: ', skyline)


skyline, comp_count=dc.divide_and_conquer(env, dimension, mcr_type)
print('DC: ', skyline)


skyline, response_time, comp_count = sfs.sort_filter_skyline(env,
                                    dimension, mcr_type)
print('SFS: ', skyline)


index_file = b_tree.sort_for_all_dimension(env, 
                                record_num, dimension, mcr_type)
skyline, response_time, comp_count = sfs.sort_filter_skyline(
                                index_file, dimension, mcr_type)
print('B-Tree: ', skyline)


skyline, response_time, comp_count =  bbs.bbs_algorithm(env,
                                    dimension,mcr_type, capacity)
print('BBS: ',skyline)

db.drop_db('bitirme_index.db', index_file)
db.drop_db(db_name, env)    