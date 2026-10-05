import heapq
import math
import time
import bitirme_database as db
import bitirme_record_comparison as rec_comp


class Node:
    def __init__(self, is_leaf=False):
        self.is_leaf = is_leaf
        self.children = [] # Eğer Leaf ise [record_id], değilse [Node]
        self.mbr = []      # [min_1, min_2, ..., max_1, max_2]
        
    def add_child(self, child_mbr, child_data):
        self.children.append((child_mbr, child_data))
        self.update_mbr(child_mbr)

    def update_mbr(self, child_mbr):
        # MBR'ı genişlet (Kapsayıcı kutuyu güncelle)
        dim = len(child_mbr) // 2
        if not self.mbr:
            self.mbr = list(child_mbr)
        else:
            for d in range(dim):
                self.mbr[d] = min(self.mbr[d], child_mbr[d])     # Min
                self.mbr[dim+d] = max(self.mbr[dim+d], child_mbr[dim+d]) # Max

# --- BASİT MBR HESAPLAMA ---
def get_record_mbr(record, dimension):
    # Bir nokta için MBR: [x, y, x, y] (Kendisi)
    coords = [record['var_' + str(d+1)] for d in range(dimension)]
    return coords + coords # [min_coords, max_coords]

def calc_l1_dist(coords):
    return sum(abs(x) for x in coords)

# --- BULK LOAD (Ağacı Oluşturma) ---
def build_simple_rtree(records, dimension, capacity):
    # 1. Base Case: Tüm kayıtlar tek düğüme sığıyorsa Root yap
    if len(records) <= capacity:
        root = Node(is_leaf=True)
        for rec in records:
            mbr = get_record_mbr(rec, dimension)
            root.add_child(mbr, rec) # Leaf düğüm veriyi (record) tutar
        return root

    # 2. Bölme (Partitioning) - Basitçe 1. boyuta göre sıralayıp bölüyoruz
    # (Daha iyisi için STR algoritması kullanılabilir ama bu yeterlidir)
    records.sort(key=lambda x: x['var_1'])
    
    num_slices = math.ceil(len(records) / capacity)
    slice_size = math.ceil(len(records) / num_slices)
    
    internal_node = Node(is_leaf=False)
    
    for i in range(num_slices):
        chunk = records[i*slice_size : (i+1)*slice_size]
        
        # Rekürsif olarak alt ağacı oluştur
        child_node = build_simple_rtree(chunk, dimension, capacity)
        
        # Oluşan alt ağacı (child_node) bu düğüme ekle
        internal_node.add_child(child_node.mbr, child_node)
        
    return internal_node


def bbs_algorithm(env, dimension, mcr_type, capacity):
    response_time = 0
    start = time.time()
    # 1. Veriyi Hazırla
    records = db.select_all(env)
    
    # 2. Ağacı İnşa Et (Root'u al)
    root = build_simple_rtree(records, dimension, capacity)
    
    skyline = []
    
    # 3. Priority Queue (Heap)
    # Yapı: (Score, MBR, Node_Data, Is_Leaf_Entry)
    heap = []
    
    # Root'u Heap'e atarak başla
    # Root bir Node objesidir.
    dist = calc_l1_dist(root.mbr[:dimension]) # Minimizasyon için sol alt köşe
    
    # Heap'e ekle: (Distance, UniqueID, MBR, Object, Is_Object)
    # UniqueID: Heap sıralamasında veri tipleri çakışmasın diye
    counter = 0 
    comp_counter = 0
    heapq.heappush(heap, (dist, counter, root.mbr, root, False))
    
    while heap:
        score, _, current_mbr, current_obj, is_real_object = heapq.heappop(heap)
        
        # --- DOMİNASYON KONTROLÜ ---
        # Elimizdeki MBR (veya Kayıt) mevcut Skyline tarafından domine ediliyor mu?
        is_dominated = False
        
        # Geçici bir kayıt sözlüğü oluştur (Kıyaslama fonksiyonu için)
        check_coords = current_mbr[:dimension] if mcr_type == 0 else current_mbr[dimension:]
        candidate_rec = { 'var_'+str(i+1): check_coords[i] for i in range(dimension) }
        
        for sky_rec in skyline:
            comp_counter += 1
            res = rec_comp.compare_records(candidate_rec, sky_rec, 
                                           dimension, mcr_type)
            if res == 2: # Skyline, adayı eziyor
                is_dominated = True
                break
        
        if is_dominated:
            continue # BU DAL KOMPLE ÇÖPE GİDER (PRUNING) - BBS'in gücü burada!

        # --- İŞLEME ---
        if is_real_object:
            # Bu gerçek bir kayıt ve domine edilmedi -> Skyline'a ekle
            skyline.append(current_obj)
            if not skyline :
                response_time = time.time() - start
                
        else:
            # Bu bir Düğüm (Kutu). İçini aç ve çocuklarını heap'e at.
            node = current_obj
            
            for child_mbr, child_data in node.children:
                counter += 1
                
                # Mesafe hesabı
                if mcr_type == 0: # Min
                    d = calc_l1_dist(child_mbr[:dimension])
                else: # Max (Negatif mesafe)
                    d = -calc_l1_dist(child_mbr[dimension:])
                
                # Eğer Node leaf ise çocukları gerçek objedir (is_real_object=True)
                is_child_object = node.is_leaf
                
                heapq.heappush(heap, (d, counter, child_mbr, child_data, is_child_object))
                
    return [rec['record_id'] for rec in skyline], response_time, comp_counter
