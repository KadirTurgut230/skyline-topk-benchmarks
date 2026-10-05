import tkinter as tk
from tkinter import font as tkfont
from bitirme_ui_comparison import ComparisonPage
from bitirme_ui_single_skyline import SingleSkylinePage
from bitirme_ui_topk import TopKPage
from bitirme_ui_plot_viewer import GalleryPage
from bitirme_ui_data_table import DataTablePage

# --- 1. EKRAN: ANA MENÜ (GÜNCELLENDİ: BÜYÜK BUTONLAR, CLOSE YOK) ---
class MainMenu(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        # Arka plan rengi
        self.configure(bg="#2c3e50")

        # Font ayarları (BÜYÜTÜLDÜ: 16 -> 24)
        button_font = tkfont.Font(family="Helvetica", size=24, weight="bold")

        # --- CLOSE BUTONU KALDIRILDI ---

        # --- ORTA ALAN: MENÜ BUTONLARI ---
        # Ortalamak için bir iç frame
        center_frame = tk.Frame(self, bg="#2c3e50")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Buton boyutları artırıldı (width=55, height=3) ve aralıklar (pady) genişletildi

        # Buton 1
        btn1 = tk.Button(center_frame, text="Comparison of Skyline Algorithms",
                         bg="white", fg="black", font=button_font,
                         width=55, height=3,
                         command=lambda: controller.show_frame("ComparisonPage"))
        btn1.pack(pady=30)

        # Buton 2
        btn2 = tk.Button(center_frame, text="Single Skyline Algorithm Execution",
                         bg="white", fg="black", font=button_font,
                         width=55, height=3,
                         command=lambda: controller.show_frame("SingleSkylinePage"))
        btn2.pack(pady=30)

        # Buton 3
        btn3 = tk.Button(center_frame, text="Top-k Query",
                         bg="white", fg="black", font=button_font,
                         width=55, height=3,
                         command=lambda: controller.show_frame("TopKPage"))
        btn3.pack(pady=30)
        
        
class SkylineApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title("Skyline & Top-k Query Interface")
        
        # --- PENCEREYİ KONUMLANDIRMA ---
        window_width = 1800
        window_height = 900
        
        screen_width = 1920
        screen_height = 1080
        
        # X tam ortada kalsın
        x_cordinate = int((screen_width / 2) - (window_width / 2))
        
        # Y'yi tam ortadan 50 piksel yukarı taşıyoruz (-50)
        y_cordinate = int((screen_height / 2) - (window_height / 2)) - 50

        # Geometry ayarı
        self.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")
        
        self.resizable(False, False)

        # Tüm ekranların tutulacağı ana konteyner
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        # Sayfaları yükle
        for F in (MainMenu, ComparisonPage, SingleSkylinePage, TopKPage, 
                  GalleryPage, DataTablePage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainMenu")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    def open_gallery(self, fig_list, records, skyline, res_control, selected_algos, source_type="comparison"):
        gallery = self.frames["GalleryPage"]
        # source_type parametresini iletiyoruz
        gallery.update_gallery(fig_list, records, skyline, res_control, selected_algos, source_type)
        self.show_frame("GalleryPage")
        
        
if __name__ == "__main__":
    app = SkylineApp()
    app.mainloop()