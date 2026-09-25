import tkinter as tk
from tkinter import ttk
from database import init_db,backend_name
from modules.dashboard import DashboardFrame
from modules.clientes import ClientesFrame
from modules.proveedores import ProveedoresFrame
from modules.inventario import InventarioFrame
from modules.ventas import VentasFrame
from modules.compras import ComprasFrame
from modules.reportes import ReportesFrame
class ERPApp(tk.Tk):
    def __init__(self,user):
        super().__init__(); self.user=user
        self.title("ERP V3 - Gestión Empresarial"); self.geometry("1180x720"); self.minsize(1000,620); self.configure(bg="#f3f5f7")
        self.style=ttk.Style(self)
        try:self.style.theme_use("clam")
        except:pass
        self.style.configure("TButton",padding=8); self.style.configure("Treeview",rowheight=28)
        self.build()
    def build(self):
        self.sidebar=ttk.Frame(self,width=210); self.sidebar.pack(side="left",fill="y")
        ttk.Label(self.sidebar,text="ERP V3",font=("Segoe UI",22,"bold")).pack(pady=(25,2))
        ttk.Label(self.sidebar,text="Gestión empresarial",font=("Segoe UI",9)).pack(pady=(0,5))
        ttk.Label(self.sidebar,text=f"👤 {self.user['usuario']} · {self.user['rol']}",font=("Segoe UI",9,"bold")).pack(pady=(0,20))
        self.content=ttk.Frame(self); self.content.pack(side="right",fill="both",expand=True)
        items=[("🏠  Dashboard",DashboardFrame),("👥  Clientes",ClientesFrame),("🚚  Proveedores",ProveedoresFrame),("📦  Inventario",InventarioFrame),("🛒  Ventas",VentasFrame),("🧾  Compras",ComprasFrame),("📊  Reportes",ReportesFrame)]
        self.frames={}
        for text,cls in items:
            ttk.Button(self.sidebar,text=text,command=lambda c=cls:self.show(c)).pack(fill="x",padx=15,pady=4); self.frames[cls]=None
        ttk.Separator(self.sidebar).pack(fill="x",padx=15,pady=20); ttk.Button(self.sidebar,text="Salir",command=self.destroy).pack(fill="x",padx=15)
        self.show(DashboardFrame)
    def show(self,cls):
        for f in self.frames.values():
            if f:f.pack_forget()
        if self.frames[cls] is None:self.frames[cls]=cls(self.content,self)
        self.frames[cls].pack(fill="both",expand=True)
        if hasattr(self.frames[cls],"refresh"):self.frames[cls].refresh()
        if cls in (VentasFrame,ComprasFrame) and hasattr(self.frames[cls],"refresh_options"):self.frames[cls].refresh_options()
    def refresh_dashboard(self):
        f=self.frames.get(DashboardFrame)
        if f:f.refresh()
        for cls in (VentasFrame,ComprasFrame):
            f=self.frames.get(cls)
            if f and hasattr(f,"refresh_options"):f.refresh_options()
def launch(user):
    app=ERPApp(user); app.mainloop()
if __name__=="__main__":
    init_db()
    root=tk.Tk(); root.withdraw()
    from modules.login import LoginFrame
    LoginFrame(root,lambda u:(root.destroy(),launch(u)))
    root.mainloop()
