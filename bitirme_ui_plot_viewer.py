import tkinter as tk
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class GalleryPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.configure(bg="white")
        
        self.figures = []
        self.current_idx = 0
        self.canvas = None
        self.stored_data = None 

        self._create_interface()

    def _create_interface(self):
        # ... (Sol/Sağ oklar, Geri butonu ve Plot Frame aynı kalsın) ...
        self.btn_prev = tk.Button(self, text="<", font=("Arial", 25, "bold"), command=self._prev_graph, bg="#e0e0e0")
        self.btn_prev.place(relx=0.01, rely=0.5, anchor="w", width=60, height=120)
        self.btn_next = tk.Button(self, text=">", font=("Arial", 25, "bold"), command=self._next_graph, bg="#e0e0e0")
        self.btn_next.place(relx=0.99, rely=0.5, anchor="e", width=60, height=120)
        self.plot_frame = tk.Frame(self, bg="white")
        self.plot_frame.place(relx=0.5, rely=0.45, anchor="center", width=1600, height=750)
        self.btn_back = tk.Button(self, text="Back", bg="red", fg="white", font=("Arial", 16, "bold"), command=self._back_action)
        self.btn_back.place(relx=0.02, rely=0.95, anchor="sw", width=160, height=60)
        self.btn_back.lift()

        # YEŞİL BUTON (Referansını saklıyoruz ki gizleyebilelim)
        self.btn_finish = tk.Button(self, text="Next Step", bg="#27ae60", fg="white", 
                                  font=("Arial", 16, "bold"), command=self._next_step_action)
        # Place işlemini update_gallery içinde dinamik yapacağız

    def update_gallery(self, figure_list, records, skyline, res_control, selected_algos, source_type):
        """
        source_type: "comparison", "single_skyline", "top_k"
        """
        self.figures = figure_list
        self.stored_data = (records, skyline, res_control, selected_algos)
        self.current_idx = 0
        
        # --- BUTON GİZLEME MANTIĞI ---
        if source_type == "single_skyline":
            # Eğer Single Skyline ise butonu kaldır
            self.btn_finish.place_forget()
        else:
            # Diğerlerinde (Comparison, Top-K) göster
            self.btn_finish.place(relx=0.98, rely=0.95, anchor="se", width=180, height=60)
            self.btn_finish.lift()

        if self.figures:
            self._show_graph()
        else:
            if self.canvas: self.canvas.get_tk_widget().destroy()

    def _show_graph(self):
        # ... (Grafik çizme kodu aynı) ...
        if self.canvas: self.canvas.get_tk_widget().destroy()
        if not self.figures: return
        fig = self.figures[self.current_idx]
        self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        self.canvas.draw()
        widget = self.canvas.get_tk_widget()
        widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas.mpl_connect('button_press_event', self._on_graph_click)

    def _next_graph(self): # ... (Aynı) ...
        if not self.figures: return
        if self.current_idx < len(self.figures) - 1: self.current_idx += 1
        else: self.current_idx = 0 
        self._show_graph()

    def _prev_graph(self): # ... (Aynı) ...
        if not self.figures: return
        if self.current_idx > 0: self.current_idx -= 1
        else: self.current_idx = len(self.figures) - 1 
        self._show_graph()

    def _on_graph_click(self, event): # ... (Aynı) ...
        if event.button == 1:
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
            if file_path: self.figures[self.current_idx].savefig(file_path)

    def _back_action(self):
        self.controller.show_frame("MainMenu")

    def _next_step_action(self):
        if self.stored_data:
            records, skyline, res_control, algos = self.stored_data
            page = self.controller.frames["DataTablePage"]
            page.display_data(records, skyline, res_control, algos)
            self.controller.show_frame("DataTablePage")