from matplotlib.figure import Figure
import pandas as pd
import textwrap
import matplotlib.pyplot as plt
# ==========================================
# 1. GÜNCELLENMİŞ GRAFİK FONKSİYONLARI
# ==========================================

def create_matrix_table(row_headers, col_headers, data_columns, title):
    # --- Hazırlık ---
    final_rows = [str(r) for r in row_headers[:6]]
    final_cols = ["\n".join(textwrap.wrap(str(c), width=12)) for c in col_headers[:4]]

    data_dict = {}
    for i, col_name in enumerate(final_cols):
        if i < len(data_columns):
            column_data = data_columns[i][:len(final_rows)]
            data_dict[col_name] = column_data
        else:
            data_dict[col_name] = [""] * len(final_rows)

    df = pd.DataFrame(data_dict, index=final_rows)

    # --- Figure Sınıfı ---
    fig = Figure(figsize=(12, 7), dpi=100) 
    # add_subplot(111) yerine kenar boşluklarını sıfırlamak için özel bir pozisyon verebiliriz
    # Ancak tight_layout kullanacağımız için 111 yeterlidir.
    ax = fig.add_subplot(111)
    
    # Eksenleri kapatıyoruz ki çizgiler görünmesin
    ax.axis('off')
    
    # Başlığı biraz daha yukarı (y=1.02) alarak tablodan uzaklaştırıyoruz
    ax.set_title(title, fontsize=22, fontweight='bold', pad=20)

    # Tablo Oluşturma
    # bbox=[0, 0, 1, 1] parametresi tabloyu eksenin tamamına yayar
    table = ax.table(cellText=df.values,
                     colLabels=df.columns,
                     rowLabels=df.index,
                     cellLoc='center',
                     loc='center')

    # --- Stil Ayarları ---
    table.auto_set_font_size(False)
    
    # Yazı boyutunu 20'den 16'ya çektim, 20 tabloyu patlatabilir.
    # Eğer 20 zorunluysa figsize=(14, 8) gibi büyütülmeli.
    font_size = 16 
    table.set_fontsize(font_size)

    cells = table.get_celld()
    for (row, col), cell in cells.items():
        if row == 0:
            cell.set_height(0.2) # Başlık yüksekliği
            cell.set_text_props(weight='bold', verticalalignment='center')
        else:
            cell.set_height(0.12) # Satır yüksekliği
        
        if col == -1: # Satır başlıkları (rowLabels)
            cell.set_text_props(weight='bold')

    # --- KRİTİK DÜZELTME ---
    # Bu komut, içeriklerin (tablo dahil) kenarlara taşmasını engeller ve ortalar.
    # pad=1.0 kenarlardan biraz boşluk bırakır.
    fig.tight_layout(pad=2.0)
    
    return fig

def create_plot(x_data, y_data, y_label_text, title_text, x_label_text="Algorithm"):
    x_subset = x_data[:6]
    y_subset = y_data[:6]
    x_subset = [str(item) for item in x_subset]

    # --- DEĞİŞİKLİK: Figure sınıfı ---
    fig = Figure(figsize=(8, 5), dpi=100)
    ax = fig.add_subplot(111)
    
    ax.plot(x_subset, y_subset, marker='o', linestyle='-', linewidth=2, markersize=8)
    
    ax.set_xlabel(x_label_text, fontsize=12, fontweight='bold')
    ax.set_ylabel(y_label_text, fontsize=12, fontweight='bold')
    ax.set_title(title_text, fontsize=14, pad=15)
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # x ekseni yazıları uzunsa döndürme (Figure içinde tick_params kullanılır)
    ax.tick_params(axis='x', rotation=45) 
    
    fig.tight_layout()
    return fig


def create_topk_plot(row_name, data_list, title="Top-k Performance"):
    """
    Performans metriklerini DEVASA bir tablo olarak çizen fonksiyon.
    data_list formatı: [[Naive_Time, Naive_Mem], [BFS_Time, BFS_Mem]]
    """
    col_headers = [
        "\n".join(textwrap.wrap("Overall Time (s)", width=15)),
        "\n".join(textwrap.wrap("Ram Usage (MB)", width=15))
    ]
    row_labels = ["SQL Naive", "Python BFS"]
    
    # Veri temizleme
    clean_data = []
    for row in data_list:
        clean_data.append([float(x) if x is not None else 0.0 for x in row])

    df = pd.DataFrame(clean_data, columns=col_headers, index=row_labels)

    # 1. DEĞİŞİKLİK: Figure boyutu büyütüldü (9,4 -> 14, 7)
    # Bu sayede 1600px genişliğindeki alana daha iyi yayılacak.
    fig = Figure(figsize=(14, 7), dpi=100)
    ax = fig.add_subplot(111)
    
    # Eksenleri kapatıyoruz ama çerçeve payı bırakıyoruz
    ax.axis('off')
    
    # Başlık boyutu artırıldı (14 -> 24)
    ax.set_title(title + f"\n({row_name})", fontsize=24, fontweight='bold', pad=30)

    # Tabloyu oluştur
    table = ax.table(cellText=df.values, colLabels=df.columns, rowLabels=df.index,
                     cellLoc='center', loc='center')
    
    # 2. DEĞİŞİKLİK: Font boyutu ve Hücre Genişliği/Yüksekliği
    table.auto_set_font_size(False)
    table.set_fontsize(20)  # Font 12 -> 20 yapıldı
    
    # Scale(Genişlik Çarpanı, Yükseklik Çarpanı)
    # Yüksekliği 1.5'tan 4'e çıkardık ki satırlar ferah olsun
    table.scale(1, 4) 
    
    # Görsel Düzenleme
    cells = table.get_celld()
    for (r, c), cell in cells.items():
        # Hücre kenar çizgilerini kalınlaştır
        cell.set_linewidth(2)
        
        # Header (Başlık) Satırı
        if r == 0: 
            cell.set_facecolor('#dcdcdc') # Biraz daha koyu gri
            cell.set_text_props(weight='bold', size=22) # Başlık fontu daha da büyük
            cell.set_height(0.15) # Başlık satırı biraz daha yüksek olsun
        
        # Row Labels (Sol taraftaki SQL/Python yazıları)
        if c == -1:
            cell.set_text_props(weight='bold', size=20)
            cell.set_facecolor('#f2f2f2')

    fig.tight_layout()
    return fig


def plot_records(data):
    """
    Verileri konsolda (pop-up pencerede) görselleştirir.
    """
    # Veri ayıklama
    x_values = [item['var_1'] for item in data]
    y_values = [item['var_2'] for item in data]
    
    # Etiketleme mantığı: rec_id veya record_id kontrolü
    labels = []
    for item in data:
        rid = item.get('record_id') or item.get('rec_id') or "Unknown_0"
        labels.append(rid.split('_')[1])
    
    # --- KONSOL İÇİN PLT KULLANIMI ---
    plt.figure(figsize=(10, 6))
    
    # Noktaları çiz
    plt.scatter(x_values, y_values, color='blue', alpha=0.7, s=100)
    
    # ID numaralarını (kırmızı etiketler) ekle
    for i, txt in enumerate(labels):
        plt.annotate(txt, (x_values[i], y_values[i]), 
                     textcoords="offset points", 
                     xytext=(5, 5), 
                     ha='left', 
                     fontsize=11, 
                     color='red')
    
    plt.xlabel('var_1')
    plt.ylabel('var_2')
    plt.title('2D Skyline Analysis')
    plt.grid(True, linestyle='--', alpha=0.5)
    
    # Grafiği ekrana bas (Konsol modunda bu şarttır)
    plt.show()