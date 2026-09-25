import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection
from modules.helpers import make_tree, clear_tree, error, money

class ComprasFrame(ttk.Frame):
    def __init__(self,parent,app):
        super().__init__(parent); self.app=app; self.cart=[]; self.build(); self.refresh_options()
    def build(self):
        top=ttk.LabelFrame(self,text="Nueva compra")
        top.pack(fill="x",padx=12,pady=12)
        self.proveedor=tk.StringVar(); self.producto=tk.StringVar(); self.cantidad=tk.StringVar(value="1"); self.precio=tk.StringVar()
        ttk.Label(top,text="Proveedor").grid(row=0,column=0,padx=5,pady=6)
        self.cb_prov=ttk.Combobox(top,textvariable=self.proveedor,state="readonly",width=28); self.cb_prov.grid(row=0,column=1)
        ttk.Label(top,text="Producto").grid(row=0,column=2,padx=5)
        self.cb_prod=ttk.Combobox(top,textvariable=self.producto,state="readonly",width=30); self.cb_prod.grid(row=0,column=3)
        ttk.Label(top,text="Cantidad").grid(row=0,column=4,padx=5); ttk.Entry(top,textvariable=self.cantidad,width=8).grid(row=0,column=5)
        ttk.Label(top,text="Precio compra").grid(row=0,column=6,padx=5); ttk.Entry(top,textvariable=self.precio,width=12).grid(row=0,column=7)
        ttk.Button(top,text="Agregar",command=self.add).grid(row=0,column=8,padx=5)
        self.tree=make_tree(self,["Código","Producto","Cantidad","Precio","Subtotal"],[100,240,90,110,130])
        bottom=ttk.Frame(self); bottom.pack(fill="x",padx=12,pady=8)
        self.total=tk.StringVar(value="$0")
        ttk.Label(bottom,text="TOTAL:",font=("Segoe UI",12,"bold")).pack(side="left")
        ttk.Label(bottom,textvariable=self.total,font=("Segoe UI",12,"bold")).pack(side="left",padx=10)
        ttk.Button(bottom,text="Registrar compra",command=self.save).pack(side="right")
    def refresh_options(self):
        conn=get_connection()
        vs=conn.execute("SELECT id,nombre FROM proveedores ORDER BY nombre").fetchall()
        ps=conn.execute("SELECT id,codigo,nombre,precio_compra FROM inventario ORDER BY nombre").fetchall(); conn.close()
        self.providers={f'{r["id"]} - {r["nombre"]}':r["id"] for r in vs}
        self.products={f'{r["id"]} - {r["codigo"]} - {r["nombre"]}':dict(r) for r in ps}
        self.cb_prov["values"]=list(self.providers); self.cb_prod["values"]=list(self.products)
    def add(self):
        try:
            p=self.products[self.producto.get()]; q=int(self.cantidad.get()); price=float(self.precio.get() or p["precio_compra"])
            if q<=0: raise ValueError()
            self.cart.append((p,q,price)); self.render()
        except Exception as e:error("Revisa producto, cantidad y precio.\n"+str(e))
    def render(self):
        clear_tree(self.tree); total=0
        for p,q,price in self.cart:
            sub=price*q; total+=sub
            self.tree.insert("", "end",values=(p["codigo"],p["nombre"],q,money(price),money(sub)))
        self.total.set(money(total))
    def save(self):
        if not self.cart:error("Agrega productos.");return
        conn=get_connection()
        try:
            pid=self.providers.get(self.proveedor.get())
            total=sum(price*q for p,q,price in self.cart)
            cur=conn.execute("INSERT INTO compras(proveedor_id,total) VALUES(?,?)",(pid,total)); cid=cur.lastrowid
            for p,q,price in self.cart:
                conn.execute("INSERT INTO compra_detalle(compra_id,producto_id,cantidad,precio) VALUES(?,?,?,?)",(cid,p["id"],q,price))
                conn.execute("UPDATE inventario SET stock=stock+?,precio_compra=? WHERE id=?",(q,price,p["id"]))
            conn.commit(); messagebox.showinfo("Compra",f"Compra #{cid} registrada por {money(total)}")
            self.cart=[]; self.render(); self.refresh_options(); self.app.refresh_dashboard()
        except Exception as e: conn.rollback(); error(str(e))
        finally: conn.close()
