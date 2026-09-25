import tkinter as tk
from tkinter import ttk
from database import get_connection
from modules.helpers import money
from database import backend_name

class DashboardFrame(ttk.Frame):
    def __init__(self,parent,app):
        super().__init__(parent); self.app=app
        self.cards={}; self.build(); self.refresh()
    def build(self):
        ttk.Label(self,text="Panel principal",font=("Segoe UI",22,"bold")).pack(anchor="w",padx=20,pady=(20,2))
        ttk.Label(self,text="Indicadores del sistema · BD activa: "+backend_name().upper()).pack(anchor="w",padx=20,pady=(0,10))
        row=ttk.Frame(self); row.pack(fill="x",padx=20,pady=10)
        for i,(key,title) in enumerate([("ventas","Ventas"),("compras","Compras"),("productos","Productos"),("clientes","Clientes")]):
            box=ttk.LabelFrame(row,text=title); box.grid(row=0,column=i,padx=7,sticky="nsew")
            row.columnconfigure(i,weight=1)
            v=tk.StringVar(value="0"); self.cards[key]=v
            ttk.Label(box,textvariable=v,font=("Segoe UI",20,"bold")).pack(padx=25,pady=20)
        low=ttk.LabelFrame(self,text="Alertas de inventario")
        low.pack(fill="both",expand=True,padx=20,pady=15)
        self.alerts=tk.Listbox(low,font=("Segoe UI",11)); self.alerts.pack(fill="both",expand=True,padx=10,pady=10)
    def refresh(self):
        conn=get_connection()
        ventas=conn.execute("SELECT COALESCE(SUM(total),0) FROM ventas").fetchone()[0]
        compras=conn.execute("SELECT COALESCE(SUM(total),0) FROM compras").fetchone()[0]
        productos=conn.execute("SELECT COUNT(*) FROM inventario").fetchone()[0]
        clientes=conn.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]
        low=conn.execute("SELECT codigo,nombre,stock,stock_minimo FROM inventario WHERE stock<=stock_minimo ORDER BY stock").fetchall()
        conn.close()
        self.cards["ventas"].set(money(ventas)); self.cards["compras"].set(money(compras))
        self.cards["productos"].set(str(productos)); self.cards["clientes"].set(str(clientes))
        self.alerts.delete(0,"end")
        if not low:self.alerts.insert("end","No hay productos por debajo del stock mínimo.")
        else:
            for r in low:self.alerts.insert("end",f'{r["codigo"]} - {r["nombre"]}: {r["stock"]} unidades (mínimo {r["stock_minimo"]})')
