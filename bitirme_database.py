import lmdb
import json
import os
import shutil
import gc 
import random
import time

def create_db(db_name, record_num, dimension, value_limit):
    map_size = (10000 + 128 * dimension) * record_num
    env = lmdb.open(db_name, map_size=map_size)
    
    with env.begin(write=True) as txn:
        
        for i in range(1, record_num + 1):
            record_id = 'record_' + str(i)
            dictionary = {'record_id' : record_id }
            
            for j in range(1, dimension + 1):
                key = 'var_' + str(j)
                value = random.randint(0, value_limit[j - 1])
                dictionary [key]= value
        
            json_dict = json.dumps(dictionary)
            txn.put(record_id.encode('utf-8'), json_dict.encode('utf-8'))
        
    return env


def create_index_file(index_name, record_list, dimension):
    map_size = (10000 + 128 * dimension) * len(record_list) 
    index_env = lmdb.open(index_name, map_size=map_size)
    
    
    with index_env.begin(write=True) as txn:
        
        for i in range(len(record_list)):
            record = record_list[i]
            record_id = record['record_id']
            json_record = json.dumps(record)
            
            txn.put(record_id.encode('utf-8'), json_record.encode('utf-8'))
        
    return index_env


def select_all(env):
    """Tüm kayıtları oku ve listeye döndür"""
    #key.decode() : json.loads(value.decode())
    kayitlar = []
    with env.begin() as txn:
        cursor = txn.cursor()
        for key, value in cursor:
            kayitlar.append(
                json.loads(value.decode())
                )
    return kayitlar
            

def print_all(env):
    """Tüm kayıtları yazdir"""
    with env.begin() as txn:
        cursor = txn.cursor()
        for key, value in cursor :
            print(json.loads(value.decode()))
    
    return

def select_one(env, record_id):
    """Record ID'sine göre tek kayıt getir"""
    with env.begin() as txn:
        key = record_id.encode()
        value = txn.get(key)

        if value:
            return json.loads(value.decode())
        else:
            return None

def print_all_attributes(env, record, dimension):
    for i in range(1, dimension + 1):
        print(record['var_' + str(i)])


def drop_db(db_name, env):    
    env.close()
    del env
    gc.collect()
    print("✅ Environment kapatıldı")
    time.sleep(0.5)
    # Dosyaları sil
    if os.path.exists(db_name):
        shutil.rmtree(db_name)
        print(f"✅ Veritabanı dosyaları silindi: {db_name}")
    else:
        print(f"⚠️  Veritabanı zaten silinmiş: {db_name}")
    

