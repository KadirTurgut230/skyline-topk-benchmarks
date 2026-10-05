import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from bitirme_test import compare_algorithms

class ComparisonPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.configure(bg="#ecf0f1")

        # Değişkenler
        self.record_num = 0
        self.dimension = 0
        self.mcr_type = False # Yeni Değişken
        self.selected_algos = []
        self.limits = []

        # --- FONT AYARLARI ---
        self.header_font = ("Helvetica", 30, "bold")
        self.input_label_font = ("Helvetica", 32)
        self.input_entry_font = ("Helvetica", 32)
        self.limit_lbl_font = ("Helvetica", 24)
        self.limit_ent_font = ("Helvetica", 26)
        self.algo_btn_font = ("Helvetica", 20, "bold") 
        self.btn_font = ("Helvetica", 20, "bold")

        # --- LAYOUT ---
        left_frame = tk.Frame(self, bg="#bdc3c7", width=650)
        left_frame.pack(side="left", fill="y", ipadx=10)
        
        right_frame = tk.Frame(self, bg="#ecf0f1")
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # --- SOL PANEL: ALGORİTMA SEÇİMİ ---
        tk.Label(left_frame, text="Select Algorithms", bg="#bdc3c7", font=self.header_font).pack(pady=(40, 20))
        self.algos = ["Naive Nested Loop (NNL)", "Block Nested Loop (BNL)", "Divide and Conquer (DC)", "Sort Filter Skyline (SFS)", "B-Tree (Index)", "Branch & Bound Skyline (BBS)"]
        self.algo_vars = []   
        self.algo_btns = []

        for i, algo_name in enumerate(self.algos):
            var = tk.BooleanVar(value=False)
            self.algo_vars.append(var)
            btn = tk.Button(left_frame, text=algo_name, font=self.algo_btn_font, width=24, height=2, bg="#ecf0f1", fg="black", activebackground="black", activeforeground="white")
            btn.config(command=lambda b=btn, v=var: self.toggle_algorithm(b, v))
            btn.pack(pady=10, padx=20)
            self.algo_btns.append(btn)
            if i == 5: self.toggle_algorithm(btn, var)

        btn_back = tk.Button(left_frame, text="Back", font=self.btn_font, bg="#c0392b", fg="white", width=20, height=2, command=lambda: controller.show_frame("MainMenu"))
        btn_back.pack(side="bottom", pady=40)

        # --- SAĞ PANEL: KONFİGÜRASYON (MCR EKLENDİ) ---
        tk.Label(right_frame, text="Configuration", bg="#ecf0f1", font=self.header_font).pack(pady=(20, 30))

        top_input_frame = tk.Frame(right_frame, bg="#ecf0f1")
        top_input_frame.pack(anchor="n", fill="x", padx=20)
        for i in range(7): top_input_frame.columnconfigure(i, weight=1)

        # SATIR 0: Records, Dimensions, Update
        tk.Label(top_input_frame, text="Records:", bg="#ecf0f1", font=self.input_label_font).grid(row=0, column=1, sticky="e", padx=15, pady=10)
        self.entry_records = tk.Entry(top_input_frame, font=self.input_entry_font, width=10)
        self.entry_records.insert(0, "1000")
        self.entry_records.grid(row=0, column=2, sticky="w", padx=15, pady=10)

        tk.Label(top_input_frame, text="Dimensions:", bg="#ecf0f1", font=self.input_label_font).grid(row=0, column=3, sticky="e", padx=15, pady=10)
        self.entry_dims = tk.Entry(top_input_frame, font=self.input_entry_font, width=10)
        self.entry_dims.insert(0, "5")
        self.entry_dims.grid(row=0, column=4, sticky="w", padx=15, pady=10)
        
        btn_update = tk.Button(top_input_frame, text="Update", command=self.create_dimension_fields, bg="#3498db", fg="white", font=self.btn_font, width=12, height=1)
        btn_update.grid(row=0, column=5, padx=20, pady=10)

        # SATIR 1: MCR Type (Records'un altına)
        tk.Label(top_input_frame, text="MCR Type:", bg="#ecf0f1", font=self.input_label_font).grid(row=1, column=1, sticky="e", padx=15, pady=10)
        
        self.mcr_combo = ttk.Combobox(top_input_frame, font=self.input_entry_font, width=9, state="readonly")
        self.mcr_combo['values'] = ("Minimized", "Maximized")
        self.mcr_combo.current(0) # Varsayılan: Minimized
        self.mcr_combo.grid(row=1, column=2, sticky="w", padx=15, pady=10)


        # --- SAĞ PANEL: SCROLL AREA ---
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

        self.dim_entries = []
        btn_confirm = tk.Button(right_frame, text="Confirm", font=self.btn_font, bg="#27ae60", fg="white", width=20, height=2, command=self.save_data) 
        btn_confirm.pack(side="bottom", anchor="e", pady=20, padx=50)

        self.create_dimension_fields()

    def toggle_algorithm(self, btn, var):
        current = var.get()
        if not current:
            var.set(True); btn.config(bg="black", fg="white")
        else:
            var.set(False); btn.config(bg="#ecf0f1", fg="black")

    def create_dimension_fields(self):
        for widget in self.scrollable_frame.winfo_children(): widget.destroy()
        self.dim_entries = []
        try: n_dims = int(self.entry_dims.get())
        except ValueError: messagebox.showerror("Error", "Dimensions must be an integer."); return

        cols = 4
        for c in range(cols * 2): self.scrollable_frame.columnconfigure(c, weight=1)
        self.canvas.itemconfig(self.canvas.create_window((0,0), window=self.scrollable_frame, anchor='nw'), width=self.canvas.winfo_width())

        for i in range(n_dims):
            row = i // cols
            col = (i % cols) * 2
            lbl = tk.Label(self.scrollable_frame, text=f"{i+1}. limit:", bg="#ecf0f1", font=self.limit_lbl_font)
            lbl.grid(row=row, column=col, sticky="e", padx=(10, 5), pady=20)
            ent = tk.Entry(self.scrollable_frame, font=self.limit_ent_font, width=8)
            ent.insert(0, "20")
            ent.grid(row=row, column=col+1, sticky="w", padx=(0, 10), pady=20)
            self.dim_entries.append(ent)
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _bound_to_mousewheel(self, event): self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    def _unbound_to_mousewheel(self, event): self.canvas.unbind_all("<MouseWheel>")
    def _on_mousewheel(self, event): self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def save_data(self):
        self.selected_algos = []
        is_any_selected = False
        for i, var in enumerate(self.algo_vars):
            if var.get(): self.selected_algos.append(i + 1); is_any_selected = True
        if not is_any_selected: messagebox.showwarning("Warning", "Please select at least one algorithm."); return

        try:
            self.record_num = int(self.entry_records.get())
            self.dimension = int(self.entry_dims.get())
            combo_val = self.mcr_combo.get()
            if combo_val == "Maximized":
                self.mcr_type = True
            else:
                self.mcr_type = False # Minimized
            self.limits = [int(entry.get()) for entry in self.dim_entries]
        except ValueError: messagebox.showerror("Error", "Check numeric fields."); return

        print("-" * 30)
        print("DATA SAVED (SCREEN 2):")
        print(f"Algos: {self.selected_algos}")
        print(f"Rec/Dim/MCR: {self.record_num} / {self.dimension} / {self.mcr_type}")
        print(f"Limits: {self.limits}")
        print("-" * 30)
        
        records, skyline, res_control, fig_list = compare_algorithms(
                                            self.record_num, self.dimension, 
                             self.mcr_type, self.limits, self.selected_algos)
        self.controller.open_gallery(fig_list, records, skyline, 
                                     res_control, self.selected_algos, 
                                     source_type="comparison")
        