import tkinter as tk
from tkinter import ttk
from database import get_connection
from modules.helpers import make_tree, clear_tree, money

class ReportesFrame(ttk.Frame):
    def __init__(self,parent,app):
        super().__init__(parent); self.app=app; self.build()
    def build(self):
        ttk.Label(self,text="Reportes",font=("Segoe UI",20,"bold")).pack(anchor="w",padx=15,pady=15)
        bar=ttk.Frame(self);bar.pack(fill="x",padx=15,pady=5)
        ttk.Button(bar,text="Ventas",command=self.ventas).pack(side="left",padx=4)
        ttk.Button(bar,text="Compras",command=self.compras).pack(side="left",padx=4)
        ttk.Button(bar,text="Inventario",command=self.inventario).pack(side="left",padx=4)
        self.tree=make_tree(self,["Columna 1","Columna 2","Columna 3","Columna 4","Columna 5"],[160]*5)
    def setcols(self,heads,rows):
        self.tree["columns"]=heads
        for c in heads:self.tree.heading(c,text=c);self.tree.column(c,width=160)
        clear_tree(self.tree)
        for r in rows:self.tree.insert("", "end",values=r)
    def ventas(self):
        conn=get_connection(); rows=conn.execute("""SELECT v.id,COALESCE(c.nombre,'Consumidor final'),v.fecha,v.total,COUNT(d.id)
                    FROM ventas v LEFT JOIN clientes c ON c.id=v.cliente_id LEFT JOIN venta_detalle d ON d.venta_id=v.id
                    GROUP BY v.id ORDER BY v.id DESC""").fetchall();conn.close()
        self.setcols(["ID","Cliente","Fecha","Total","Ítems"],[(r[0],r[1],r[2],money(r[3]),r[4]) for r in rows])
    def compras(self):
        conn=get_connection(); rows=conn.execute("""SELECT c.id,COALESCE(p.nombre,'Sin proveedor'),c.fecha,c.total,COUNT(d.id)
                    FROM compras c LEFT JOIN proveedores p ON p.id=c.proveedor_id LEFT JOIN compra_detalle d ON d.compra_id=c.id
                    GROUP BY c.id ORDER BY c.id DESC""").fetchall();conn.close()
        self.setcols(["ID","Proveedor","Fecha","Total","Ítems"],[(r[0],r[1],r[2],money(r[3]),r[4]) for r in rows])
    def inventario(self):
        conn=get_connection(); rows=conn.execute("SELECT codigo,nombre,categoria,stock,precio_venta FROM inventario ORDER BY nombre").fetchall();conn.close()
        self.setcols(["Código","Producto","Categoría","Stock","Precio venta"],[(r[0],r[1],r[2],r[3],money(r[4])) for r in rows])
