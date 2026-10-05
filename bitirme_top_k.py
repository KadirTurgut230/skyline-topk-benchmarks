import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import psycopg2
import numpy as np
import heapq
import time
import sys
from bitirme_plotter import create_topk_plot

#DATABASE SETTINGS
conn_params = {
    "dbname": "postgres", "user": "postgres", "password": "1234", "host": "localhost", "port": "5432"
}


class RTreeNode:
    __slots__ = ['min_bounds', 'max_bounds', 'children', 'data_point', 'record_id']
    def __init__(self, min_bounds, max_bounds, children=None, data_point=None, record_id=None):
        self.min_bounds = min_bounds 
        self.max_bounds = max_bounds
        self.children = children if children is not None else []
        self.data_point = data_point
        self.record_id = record_id
    def is_leaf(self):
        return self.data_point is not None


def build_rtree_round_robin(nodes, max_capacity=50, depth=0):
    count = len(nodes)
    if count <= max_capacity:
        mins = np.vstack([n.min_bounds for n in nodes])
        maxs = np.vstack([n.max_bounds for n in nodes])
        return RTreeNode(np.min(mins, axis=0), np.max(maxs, axis=0), children=nodes)
    axis = depth % len(nodes[0].min_bounds)
    nodes.sort(key=lambda n: n.min_bounds[axis])
    next_level = []
    for i in range(0, count, max_capacity):
        group = nodes[i : i + max_capacity]
        mins = np.vstack([n.min_bounds for n in group])
        maxs = np.vstack([n.max_bounds for n in group])
        next_level.append(RTreeNode(np.min(mins, axis=0), np.max(maxs, axis=0), children=group))
    return build_rtree_round_robin(next_level, max_capacity, depth + 1)

# BFS SEARCHING
def run_fast_python_bfs(root, weights, k, mcr_type=True):
    pq = []
    counter = 0 
    
    if mcr_type: 
        initial_score = np.dot(root.max_bounds, weights)
        heapq.heappush(pq, (-initial_score, counter, root)) 
    else:
        initial_score = np.dot(root.min_bounds, weights)
        heapq.heappush(pq, (initial_score, counter, root)) 
    
    results = []
    
    while pq and len(results) < k:
        score, _, node = heapq.heappop(pq)
        
        if node.is_leaf():
            real_score = -score if mcr_type else score
            results.append((node.record_id, round(float(real_score), 5)))
            continue

        children = node.children
        if not children: continue

        if children[0].is_leaf():
            points_matrix = np.vstack([c.data_point for c in children])
        else:
            if mcr_type:
                points_matrix = np.vstack([c.max_bounds for c in children])
            else:
                points_matrix = np.vstack([c.min_bounds for c in children])
            
        child_scores = np.dot(points_matrix, weights)
        
        for i, child in enumerate(children):
            counter += 1
            if mcr_type:
                heapq.heappush(pq, (-child_scores[i], counter, child))
            else:
                heapq.heappush(pq, (child_scores[i], counter, child))
                
    return results

#  ANALYSIS FUNCTION
def run_full_analysis(record_num, dimension, k_value, value_limit, grades, mcr_type=True):
    conn = psycopg2.connect(**conn_params)
    conn.autocommit = True
    cur = conn.cursor()

    try:
        # 1. SQL TABLO OLUŞTURMA
        cur.execute("SELECT create_top_k_table(%s, %s, %s);", (record_num, dimension, value_limit))
        
        # 2. NAIVE TEST (SQL)
        naive_query = "SELECT * FROM top_k_query('top_k_table', %s, %s, %s);"
        
        cur.execute(f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {naive_query}", (grades, k_value, mcr_type))
        n_plan = cur.fetchone()[0][0]
        n_time = n_plan['Execution Time'] / 1000.0
        n_mem = ((n_plan['Plan'].get('Shared Hit Blocks', 0) + n_plan['Plan'].get('Shared Read Blocks', 0)) * 8) / 1024.0
        
        cur.execute(naive_query, (grades, k_value, mcr_type))
        naive_top_k = [(r[0], float(r[1])) for r in cur.fetchall()]

        # 3. BFS TEST (PYTHON)
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'top_k_table' AND column_name LIKE 'var_%' ORDER BY ordinal_position")
        col_str = ", ".join([r[0] for r in cur.fetchall()])
        cur.execute(f"SELECT record_id, {col_str} FROM top_k_table")
        raw_rows = cur.fetchall() # (record_id, var_1, var_2...)
        
        ids = np.array([r[0] for r in raw_rows])
        data_matrix = np.array([r[1:] for r in raw_rows], dtype=float)
        min_vals, max_vals = data_matrix.min(axis=0), data_matrix.max(axis=0)
        ranges = np.where((max_vals - min_vals) == 0, 1, max_vals - min_vals)
        normalized_matrix = (data_matrix - min_vals) / ranges
        
        node_list = [RTreeNode(pt, pt, data_point=pt, record_id=ids[i]) for i, pt in enumerate(normalized_matrix)]
        start_bfs = time.perf_counter()
        root = build_rtree_round_robin(node_list, max_capacity=50)
        
        bfs_results_raw = run_fast_python_bfs(root, np.array(grades), k_value, mcr_type=mcr_type)
        
        if mcr_type: 
             bfs_top_k = sorted(bfs_results_raw, key=lambda x: -x[1])
        else: 
             bfs_top_k = sorted(bfs_results_raw, key=lambda x: x[1])
        
        bfs_time = time.perf_counter() - start_bfs
        bfs_mem = sys.getsizeof(normalized_matrix) / (1024 * 1024)

        # 4. KONSOL BİLGİSİ
        print("-" * 50)
        print(f"ANALİZ (N={record_num}, K={k_value}, Mod={'Max' if mcr_type else 'Min'})")
        print(f"SQL Süre : {n_time:.4f}s | RAM: {n_mem:.2f} MB")
        print(f"BFS Süre : {bfs_time:.4f}s | RAM: {bfs_mem:.2f} MB")
        print("-" * 50)

        # 5. VALIDASYON
        validation_result = True
        
        if len(naive_top_k) != len(bfs_top_k):
            validation_result = False
        else:
            for i in range(len(naive_top_k)):
                s_id, s_score = naive_top_k[i]
                b_id, b_score = bfs_top_k[i]
                
                scores_match = abs(s_score - b_score) < 0.00001
                
                if s_id == b_id: continue 
                elif scores_match: continue
                else:
                    validation_result = False
                    print(f"✖ UYUŞMAZLIK @ Index {i}: SQL={s_id} vs BFS={b_id}")
                    break
        
        if validation_result: print("✔ DOĞRULAMA BAŞARILI")

        top_k_results = [naive_top_k, bfs_top_k]
        perf_metrics = [[round(n_time, 4), round(n_mem, 2)], [round(bfs_time, 4), round(bfs_mem, 2)]]
        
        fig = create_topk_plot(f"N={record_num}, K={k_value}", perf_metrics)
        
        return raw_rows, top_k_results, validation_result, fig

    except Exception as e:
        print(f"Hata: {e}")
        import traceback
        traceback.print_exc()
        return None, None, False, None
    finally:
        if cur: cur.close()
        if conn: conn.close()
