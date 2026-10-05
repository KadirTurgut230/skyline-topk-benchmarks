import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from bitirme_test_2 import single_skyline_algorithm

class SingleSkylinePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.configure(bg="#ecf0f1")

        self.selected_algo_id = 6
        self.data_matrix = []
        self.limits = []
        self.mcr_type = False 

        # Fontlar
        self.header_font = ("Helvetica", 30, "bold")
        self.col_header_font = ("Helvetica", 24, "bold") 
        self.row_lbl_font = ("Helvetica", 24, "bold")    
        self.input_entry_font = ("Helvetica", 28)        
        self.limit_lbl_font = ("Helvetica", 24)
        self.limit_ent_font = ("Helvetica", 26)
        self.algo_btn_font = ("Helvetica", 20, "bold") 
        self.btn_font = ("Helvetica", 20, "bold")

        left_frame = tk.Frame(self, bg="#bdc3c7", width=650)
        left_frame.pack(side="left", fill="y", ipadx=10)
        right_frame = tk.Frame(self, bg="#ecf0f1")
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # SOL PANEL
        tk.Label(left_frame, text="Select Algorithm", bg="#bdc3c7", font=self.header_font).pack(pady=(40, 20))
        self.algos = ["Naive Nested Loop (NNL)", "Block Nested Loop (BNL)", "Divide and Conquer (DC)", "Sort Filter Skyline (SFS)", "B-Tree (Index)", "Branch & Bound Skyline (BBS)"]
        self.algo_btns = []
        for i, algo_name in enumerate(self.algos):
            btn = tk.Button(left_frame, text=algo_name, font=self.algo_btn_font, width=24, height=2, bg="#ecf0f1", fg="black", activebackground="black", activeforeground="white")
            btn.config(command=lambda idx=i: self.select_algorithm(idx))
            btn.pack(pady=10, padx=20)
            self.algo_btns.append(btn)
        self.select_algorithm(5)

        btn_back = tk.Button(left_frame, text="Back", font=self.btn_font, bg="#c0392b", fg="white", width=20, height=2, command=lambda: controller.show_frame("MainMenu"))
        btn_back.pack(side="bottom", pady=40)

        # SAĞ PANEL
        tk.Label(right_frame, text="Data Configurations", bg="#ecf0f1", font=self.header_font).pack(pady=(20, 20))
        input_container = tk.Frame(right_frame, bg="#ecf0f1")
        input_container.pack(anchor="n", fill="x", padx=50)

        # Başlıklar
        tk.Label(input_container, text="#", bg="#ecf0f1", font=self.col_header_font).grid(row=0, column=0, padx=10, pady=5)
        tk.Label(input_container, text="Records", bg="#ecf0f1", font=self.col_header_font).grid(row=0, column=1, padx=20, pady=5)
        tk.Label(input_container, text="Dimensions", bg="#ecf0f1", font=self.col_header_font).grid(row=0, column=2, padx=20, pady=5)
        tk.Label(input_container, text="MCR Type", bg="#ecf0f1", font=self.col_header_font).grid(row=0, column=3, padx=20, pady=5)

        self.pair_entries = []
        self.mcr_combo_3 = None 

        for i in range(5):
            tk.Label(input_container, text=f"{i+1}", bg="#ecf0f1", font=self.row_lbl_font).grid(row=i+1, column=0, padx=10, pady=10)
            ent_rec = tk.Entry(input_container, font=self.input_entry_font, width=14, justify="center")
            ent_rec.grid(row=i+1, column=1, padx=20, pady=10)
            ent_dim = tk.Entry(input_container, font=self.input_entry_font, width=14, justify="center")
            ent_dim.grid(row=i+1, column=2, padx=20, pady=10)

            if i == 0:
                ent_rec.insert(0, "1000")
                ent_dim.insert(0, "5")
                
                # SADECE 1. SATIRA COMBOBOX
                self.mcr_combo_3 = ttk.Combobox(input_container, font=self.input_entry_font, width=12, state="readonly")
                self.mcr_combo_3['values'] = ("Minimized", "Maximized")
                self.mcr_combo_3.current(0)
                self.mcr_combo_3.grid(row=i+1, column=3, padx=20, pady=10)
            
            self.pair_entries.append([ent_rec, ent_dim])

        # UPDATE BUTONU (5. Satırın yanına taşındı: row=5)
        btn_update = tk.Button(input_container, text="Update", command=self.create_limit_fields, bg="#3498db", fg="white", font=self.btn_font, width=10, height=1)
        btn_update.grid(row=5, column=3, padx=30) 

        # SCROLL AREA
        scroll_container = tk.Frame(right_frame, bg="#ecf0f1")
        scroll_container.pack(fill="both", expand=True, pady=(20, 10))
        self.canvas = tk.Canvas(scroll_container, bg="#ecf0f1", highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar = tk.Scrollbar(scroll_container, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.scrollable_frame = tk.Frame(self.canvas, bg="#ecf0f1")
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.scrollable_frame.bind("<Enter>", self._bound_to_mousewheel)
        self.scrollable_frame.bind("<Leave>", self._unbound_to_mousewheel)

        self.limit_entries = []
        btn_confirm = tk.Button(right_frame, text="Confirm", font=self.btn_font, bg="#27ae60", fg="white", width=20, height=2, command=self.save_data) 
        btn_confirm.pack(side="bottom", anchor="e", pady=20, padx=50)

        self.create_limit_fields()

    def select_algorithm(self, idx):
        self.selected_algo_id = idx + 1
        for i, btn in enumerate(self.algo_btns):
            if i == idx: btn.config(bg="black", fg="white")
            else: btn.config(bg="#ecf0f1", fg="black")

    def create_limit_fields(self):
        for widget in self.scrollable_frame.winfo_children(): widget.destroy()
        self.limit_entries = []
        max_dim = 0
        for rec_ent, dim_ent in self.pair_entries:
            d_val = dim_ent.get()
            if d_val.strip().isdigit():
                d = int(d_val)
                if d > max_dim: max_dim = d
        if max_dim == 0: return

        cols = 4
        for c in range(cols * 2): self.scrollable_frame.columnconfigure(c, weight=1)
        self.canvas.itemconfig(self.canvas.create_window((0,0), window=self.scrollable_frame, anchor='nw'), width=self.canvas.winfo_width())

        for i in range(max_dim):
            row = i // cols
            col = (i % cols) * 2
            lbl = tk.Label(self.scrollable_frame, text=f"{i+1}. limit:", bg="#ecf0f1", font=self.limit_lbl_font)
            lbl.grid(row=row, column=col, sticky="e", padx=(10, 5), pady=20)
            ent = tk.Entry(self.scrollable_frame, font=self.limit_ent_font, width=8)
            ent.insert(0, "20")
            ent.grid(row=row, column=col+1, sticky="w", padx=(0, 10), pady=20)
            self.limit_entries.append(ent)
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _bound_to_mousewheel(self, event): self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    def _unbound_to_mousewheel(self, event): self.canvas.unbind_all("<MouseWheel>")
    def _on_mousewheel(self, event): self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def save_data(self):
        self.data_matrix = []
        for rec_ent, dim_ent in self.pair_entries:
            r_val = rec_ent.get(); d_val = dim_ent.get()
            if r_val.strip().isdigit() and d_val.strip().isdigit():
                self.data_matrix.append([int(r_val), int(d_val)])
        
        if not self.data_matrix: messagebox.showerror("Error", "Enter valid Rec/Dim."); return
        try:
            self.limits = [int(ent.get()) for ent in self.limit_entries]
            combo_val = self.mcr_combo_3.get()
            if combo_val == "Maximized":
                self.mcr_type = True
            else:
                self.mcr_type = False # Minimized 
        except ValueError: messagebox.showerror("Error", "Check inputs."); return

        print("-" * 30)
        print("DATA SAVED (SCREEN 3):")
        print(f"Algo ID: {self.selected_algo_id}")
        print(f"MCR Type: {self.mcr_type}")
        print(f"Data Matrix: {self.data_matrix}")
        print(f"Limits: {self.limits}")
        print("-" * 30)
        #messagebox.showinfo("Success", "Configuration saved!")
        records, skyline, fig_list = single_skyline_algorithm(
                                    self.data_matrix, self.mcr_type, 
                                    self.limits, self.selected_algo_id)
        self.controller.open_gallery(fig_list, records, skyline, None, 
                                     [self.selected_algo_id], 
                                     source_type="single_skyline")