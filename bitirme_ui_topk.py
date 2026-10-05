import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from bitirme_top_k import run_full_analysis

# --- 4. EKRAN: TOP-K QUERY (LAYOUT DÜZELTİLDİ, VALUE LIMIT DİZİ OLARAK GİDİYOR) ---
class TopKPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.configure(bg="#bdc3c7")

        # Değişkenler
        self.record_num = 0
        self.dimension = 0
        self.k_value = 10 
        self.mcr_type = False
        self.limits = []
        self.weights = []

        # --- FONT AYARLARI ---
        self.btn_font = ("Helvetica", 20, "bold")
        self.header_font = ("Helvetica", 40, "bold")
        self.input_label_font = ("Helvetica", 32, "bold")
        self.input_entry_font = ("Helvetica", 32)
        self.list_header_font = ("Helvetica", 28, "bold")
        self.list_row_font = ("Helvetica", 26)

        # --- LAYOUT ---
        top_frame = tk.Frame(self, bg="#bdc3c7")
        top_frame.pack(side="top", fill="x", pady=10, padx=20)

        tk.Label(top_frame, text="Top-k Query Configuration", bg="#bdc3c7", font=self.header_font).pack(side="top", pady=(10, 30))

        # Girdilerin olduğu ana kutu
        input_container = tk.Frame(top_frame, bg="#bdc3c7")
        input_container.pack(anchor="center")

        # --- SATIR 1: Records | Dimensions | K Value ---
        
        # 1. Records
        tk.Label(input_container, text="Records:", bg="#bdc3c7", font=self.input_label_font).grid(row=0, column=0, padx=(0, 10), pady=10)
        self.entry_records = tk.Entry(input_container, font=self.input_entry_font, width=8, justify="center")
        self.entry_records.insert(0, "1000")
        self.entry_records.grid(row=0, column=1, padx=(0, 40), pady=10)

        # 2. Dimensions
        tk.Label(input_container, text="Dimensions:", bg="#bdc3c7", font=self.input_label_font).grid(row=0, column=2, padx=(0, 10), pady=10)
        self.entry_dims = tk.Entry(input_container, font=self.input_entry_font, width=8, justify="center")
        self.entry_dims.insert(0, "5")
        self.entry_dims.grid(row=0, column=3, padx=(0, 40), pady=10)

        # 3. K Value
        tk.Label(input_container, text="K Value:", bg="#bdc3c7", font=self.input_label_font).grid(row=0, column=4, padx=(0, 10), pady=10)
        self.entry_k = tk.Entry(input_container, font=self.input_entry_font, width=6, justify="center")
        self.entry_k.insert(0, "10")
        self.entry_k.grid(row=0, column=5, padx=(0, 10), pady=10)


        # --- SATIR 2: MCR Type | Update Button ---
        
        # 4. MCR Type (Bir alt satıra alındı)
        tk.Label(input_container, text="MCR Type:", bg="#bdc3c7", font=self.input_label_font).grid(row=1, column=1, padx=(0, 10), pady=20, sticky="e")
        
        self.option_add("*TCombobox*Listbox*Font", self.input_entry_font)
        self.mcr_combo = ttk.Combobox(input_container, font=self.input_entry_font, width=12, state="readonly")
        self.mcr_combo['values'] = ("Minimized", "Maximized")
        self.mcr_combo.current(0)
        self.mcr_combo.grid(row=1, column=2, padx=(0, 40), pady=20, sticky="w")

        # 5. Update Butonu
        btn_update = tk.Button(input_container, text="Update", command=self.create_dynamic_fields, 
                               bg="#2980b9", fg="white", font=self.btn_font, width=12)
        btn_update.grid(row=1, column=4, columnspan=2, pady=20, sticky="w")


        # --- ORTA PANEL: SCROLL AREA ---
        headers_frame = tk.Frame(self, bg="#bdc3c7")
        headers_frame.pack(fill="x", padx=100, pady=(20, 0))
        
        headers_frame.columnconfigure(0, weight=1)
        headers_frame.columnconfigure(1, weight=1)
        headers_frame.columnconfigure(2, weight=1)

        tk.Label(headers_frame, text="Dim Index", bg="#bdc3c7", font=self.list_header_font).grid(row=0, column=0)
        tk.Label(headers_frame, text="Value Limit", bg="#bdc3c7", font=self.list_header_font).grid(row=0, column=1)
        tk.Label(headers_frame, text="Weight (Sum=1.0)", bg="#bdc3c7", font=self.list_header_font).grid(row=0, column=2)

        scroll_container = tk.Frame(self, bg="#bdc3c7")
        scroll_container.pack(fill="both", expand=True, pady=10, padx=50)

        self.canvas = tk.Canvas(scroll_container, bg="#bdc3c7", highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(scroll_container, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.scrollable_frame = tk.Frame(self.canvas, bg="#bdc3c7")
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        self.scrollable_frame.bind("<Enter>", self._bound_to_mousewheel)
        self.scrollable_frame.bind("<Leave>", self._unbound_to_mousewheel)

        self.limit_entries = []
        self.weight_entries = []

        # --- ALT PANEL: BUTONLAR ---
        bottom_frame = tk.Frame(self, bg="#bdc3c7")
        bottom_frame.pack(side="bottom", fill="x", padx=50, pady=30)

        btn_back = tk.Button(bottom_frame, text="Back", font=self.btn_font,
                             bg="#c0392b", fg="white", width=20, height=2,
                             command=lambda: controller.show_frame("MainMenu"))
        btn_back.pack(side="left")

        btn_confirm = tk.Button(bottom_frame, text="Confirm", font=self.btn_font,
                                bg="#27ae60", fg="white", width=20, height=2,
                                command=self.save_data)
        btn_confirm.pack(side="right")

        self.create_dynamic_fields()

    def create_dynamic_fields(self):
        for widget in self.scrollable_frame.winfo_children(): widget.destroy()
        self.limit_entries = []
        self.weight_entries = []

        try:
            n_dims = int(self.entry_dims.get())
        except ValueError:
            messagebox.showerror("Error", "Dimensions must be an integer.")
            return

        self.scrollable_frame.columnconfigure(0, weight=1)
        self.scrollable_frame.columnconfigure(1, weight=1)
        self.scrollable_frame.columnconfigure(2, weight=1)
        self.canvas.itemconfig(self.canvas.create_window((0,0), window=self.scrollable_frame, anchor='nw'), width=self.canvas.winfo_width())

        default_weight = 1.0 / n_dims if n_dims > 0 else 0

        for i in range(n_dims):
            lbl = tk.Label(self.scrollable_frame, text=f"{i+1}", bg="#bdc3c7", font=self.list_row_font)
            lbl.grid(row=i, column=0, pady=15)

            ent_limit = tk.Entry(self.scrollable_frame, font=self.list_row_font, width=12, justify="center")
            ent_limit.insert(0, "20")
            ent_limit.grid(row=i, column=1, pady=15)
            self.limit_entries.append(ent_limit)

            ent_weight = tk.Entry(self.scrollable_frame, font=self.list_row_font, width=12, justify="center")
            ent_weight.insert(0, f"{default_weight:.4f}") 
            ent_weight.grid(row=i, column=2, pady=15)
            self.weight_entries.append(ent_weight)

        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _bound_to_mousewheel(self, event): self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    def _unbound_to_mousewheel(self, event): self.canvas.unbind_all("<MouseWheel>")
    def _on_mousewheel(self, event): self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def save_data(self):
        try:
            self.record_num = int(self.entry_records.get())
            self.dimension = int(self.entry_dims.get())
            self.k_value = int(self.entry_k.get()) 
            
            combo_val = self.mcr_combo.get()
            self.mcr_type = True if combo_val == "Maximized" else False
            
            temp_limits = []
            temp_weights = []
            
            for ent in self.limit_entries: temp_limits.append(int(ent.get()))
            
            total_weight = 0.0
            for ent in self.weight_entries:
                w = float(ent.get())
                temp_weights.append(w)
                total_weight += w
            
            if abs(total_weight - 1.0) > 0.001:
                messagebox.showerror("Validation Error", f"Total weights must equal 1.0.\nCurrent Sum: {total_weight:.4f}")
                return

            self.limits = temp_limits # LİSTE BURADA OLUŞUYOR
            self.weights = temp_weights

            print("-" * 30)
            print("Starting Top-k Analysis...")

            # --- DEĞİŞİKLİK BURADA: self.limits (Liste) OLARAK GÖNDERİLİYOR ---
            # value_limit parametresine artık self.limits (dizi) gidiyor.
            
            raw_rows, top_k_results, validation_result, fig = run_full_analysis(
                self.record_num,
                self.dimension,
                self.k_value,
                self.limits, # LİSTE GÖNDERİLİYOR
                self.weights,
                self.mcr_type
            )

            if fig is None:
                messagebox.showerror("Error", "Analysis failed. Check console.")
                return

            # VERİ DÖNÜŞÜMÜ
            formatted_records = []
            if raw_rows:
                for row in raw_rows:
                    rec_dict = {'record_id': row[0]}
                    for idx, val in enumerate(row[1:]):
                        rec_dict[f'var_{idx+1}'] = val
                    formatted_records.append(rec_dict)

            formatted_skyline = []
            for res_list in top_k_results:
                # res_list şuna benzer: [('record_5', 0.28), ('record_10', 0.35)]
                # Artık sadece [0] alıp ID'yi almıyoruz, tüm tuple'ı listeye ekliyoruz.
                formatted_skyline.append(res_list) 

            dummy_algos = [1, 6] 

            # open_gallery'e source_type="top_k" gönderiyoruz
            self.controller.open_gallery(
                [fig], 
                formatted_records,
                formatted_skyline,
                validation_result,
                dummy_algos,
                source_type="top_k" # ÖNEMLİ
            )
            
        except ValueError: messagebox.showerror("Error", "Check numeric inputs."); return