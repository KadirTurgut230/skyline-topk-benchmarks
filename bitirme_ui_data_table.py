import tkinter as tk
from tkinter import ttk, messagebox

class DataTablePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.configure(bg="#ecf0f1")

        self.header_font = ("Helvetica", 28, "bold")
        self.label_font = ("Helvetica", 20, "bold")
        self._create_widgets()

    def _create_widgets(self):
        # ... (Üst kısımlar aynı) ...
        self.status_frame = tk.Frame(self, bg="#ecf0f1")
        self.status_frame.pack(side="top", fill="x", padx=60, pady=30)
        self.light_canvas = tk.Canvas(self.status_frame, width=60, height=60, bg="#ecf0f1", highlightthickness=0)
        self.light_canvas.pack(side="left")
        self.res_label = tk.Label(self.status_frame, text="", font=("Helvetica", 24, "bold"), bg="#ecf0f1")
        self.res_label.pack(side="left", padx=20)

        # ORTA: Records Tablosu (Aynı)
        tk.Label(self, text="Database Records", font=self.header_font, bg="#ecf0f1").pack(pady=(10, 10))
        table_container = tk.Frame(self)
        table_container.pack(expand=True, fill="both", padx=60, pady=10)
        style = ttk.Style()
        style.configure("Treeview", font=("Helvetica", 14), rowheight=35)
        style.configure("Treeview.Heading", font=("Helvetica", 16, "bold"))
        self.tree = ttk.Treeview(table_container, show="headings")
        vsb = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)

        # --- DEĞİŞİKLİK 1: BAŞLIK GENEL YAPILDI ---
        self.lbl_results = tk.Label(self, text="Algorithm Results", font=self.header_font, bg="#ecf0f1")
        self.lbl_results.pack(pady=(25, 10))
        
        self.skyline_text = tk.Text(self, height=7, font=("Consolas", 16), bg="white", padx=20, pady=20, relief="flat")
        self.skyline_text.pack(fill="x", padx=60, pady=(0, 30))

        btn_back = tk.Button(self, text="Back to Gallery", bg="#c0392b", fg="white", 
                             font=("Arial", 16, "bold"), width=18, height=2,
                             command=lambda: self.controller.show_frame("GalleryPage"))
        btn_back.place(relx=0.02, rely=0.97, anchor="sw")

    def display_data(self, records, results_data, result_control, selected_algos):
        """
        results_data: Skyline için ['rec1', 'rec2']
                      Top-K için [('rec1', 0.25), ('rec2', 0.10)]
        """
        # 1. Işık Mantığı (Aynı)
        self.light_canvas.delete("all")
        if result_control is None:
            self.res_label.config(text="")
        else:
            color = "#2ecc71" if result_control else "#e74c3c"
            self.res_label.config(text=f"Result: {result_control}", fg=color)
            self.light_canvas.create_oval(5, 5, 55, 55, fill="white", outline=color, width=2)
            self.light_canvas.create_oval(10, 10, 50, 50, fill=color, outline=color)

        # 2. Tabloyu Doldur (Aynı)
        sorted_records = sorted(records, key=lambda x: int(x['record_id'].split('_')[1]))
        self.tree.delete(*self.tree.get_children())
        if sorted_records:
            cols = list(sorted_records[0].keys())
            self.tree["columns"] = cols
            for col in cols:
                self.tree.heading(col, text=col.upper())
                self.tree.column(col, width=180, anchor="center")
            for row_data in sorted_records:
                self.tree.insert("", "end", values=list(row_data.values()))

        # 3. SONUÇLARI YAZDIR (DEĞİŞİKLİK BURADA)
        self.skyline_text.config(state="normal")
        self.skyline_text.delete("1.0", tk.END)
        
        # Algoritma isimleri haritası
        # Dikkat: TopKPage'den dummy_algos=[1, 6] geliyor (SQL, BBS/BFS)
        algo_map = {1: "NNL", 2: "BNL", 3: "DC", 4: "SFS", 5: "B-Tree", 6: "R-Tree(BBS)"}
        
        for idx, algo_id in enumerate(selected_algos):
            algo_name = algo_map.get(algo_id, f"Algo {algo_id}")
            
            # Gelen veri listesi (Skyline veya Top-K listesi)
            current_result_list = results_data[idx]
            
            # Veriyi formatla
            formatted_items = []
            for item in current_result_list:
                if isinstance(item, (list, tuple)):
                    # Top-K Durumu: ('record_5', 0.28) -> "record_5 (0.28)"
                    formatted_items.append(f"{item[0]} ({item[1]})")
                else:
                    # Skyline Durumu: 'record_5' -> "record_5"
                    formatted_items.append(str(item))
            
            result_str = ", ".join(formatted_items)
            
            self.skyline_text.insert(tk.END, f"● {algo_name}: ", "bold_tag")
            self.skyline_text.insert(tk.END, f"{result_str}\n\n")
        
        self.skyline_text.tag_configure("bold_tag", font=("Consolas", 16, "bold"))
        self.skyline_text.config(state="disabled")