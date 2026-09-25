import tkinter as tk
from tkinter import ttk,messagebox
from pathlib import Path
from database import get_connection
from modules.helpers import make_tree,clear_tree,error,money
class VentasFrame(ttk.Frame):
    def __init__(self,parent,app):
        super().__init__(parent);self.app=app;self.cart=[];self.build();self.refresh_options()
    def build(self):
        top=ttk.LabelFrame(self,text="Nueva venta");top.pack(fill="x",padx=12,pady=12)
        self.cliente=tk.StringVar();self.producto=tk.StringVar();self.cantidad=tk.StringVar(value="1")
        ttk.Label(top,text="Cliente").grid(row=0,column=0,padx=5,pady=6);self.cb_cliente=ttk.Combobox(top,textvariable=self.cliente,state="readonly",width=28);self.cb_cliente.grid(row=0,column=1)
        ttk.Label(top,text="Producto").grid(row=0,column=2,padx=5);self.cb_producto=ttk.Combobox(top,textvariable=self.producto,state="readonly",width=30);self.cb_producto.grid(row=0,column=3)
        ttk.Label(top,text="Cantidad").grid(row=0,column=4,padx=5);ttk.Entry(top,textvariable=self.cantidad,width=8).grid(row=0,column=5);ttk.Button(top,text="Agregar",command=self.add).grid(row=0,column=6,padx=5)
        self.cart_tree=make_tree(self,["Código","Producto","Cantidad","Precio","Subtotal"],[100,240,90,110,130])
        bottom=ttk.Frame(self);bottom.pack(fill="x",padx=12,pady=8);self.total=tk.StringVar(value="$0");ttk.Label(bottom,text="TOTAL:",font=("Segoe UI",12,"bold")).pack(side="left");ttk.Label(bottom,textvariable=self.total,font=("Segoe UI",12,"bold")).pack(side="left",padx=10)
        ttk.Button(bottom,text="Registrar venta / Facturar",command=self.save).pack(side="right")
        ttk.Button(bottom,text="Limpiar carrito",command=self.clear_cart).pack(side="right",padx=8)
    def refresh_options(self):
        c=get_connection();cs=c.execute("SELECT id,nombre FROM clientes ORDER BY nombre").fetchall();ps=c.execute("SELECT id,codigo,nombre,precio_venta,stock FROM inventario WHERE stock>0 ORDER BY nombre").fetchall();c.close()
        self.clients={f'{r["id"]} - {r["nombre"]}':r["id"] for r in cs};self.products={f'{r["id"]} - {r["codigo"]} - {r["nombre"]}':dict(r) for r in ps};self.cb_cliente["values"]=list(self.clients);self.cb_producto["values"]=list(self.products)
    def add(self):
        try:
            p=self.products[self.producto.get()];q=int(self.cantidad.get())
            if q<=0 or q>p["stock"]:raise ValueError("Stock insuficiente.")
            self.cart.append((p,q));self.render()
        except Exception as e:error(str(e))
    def render(self):
        clear_tree(self.cart_tree);total=0
        for p,q in self.cart:
            sub=float(p["precio_venta"])*q;total+=sub;self.cart_tree.insert("","end",values=(p["codigo"],p["nombre"],q,money(p["precio_venta"]),money(sub)))
        self.total.set(money(total))
    def save(self):
        if not self.cart:error("Agrega al menos un producto.");return
        c=get_connection()
        try:
            cid=self.clients.get(self.cliente.get());total=sum(float(p["precio_venta"])*q for p,q in self.cart)
            cur=c.execute("INSERT INTO ventas(cliente_id,total) VALUES(?,?)",(cid,total));vid=cur.lastrowid
            for p,q in self.cart:
                c.execute("INSERT INTO venta_detalle(venta_id,producto_id,cantidad,precio) VALUES(?,?,?,?)",(vid,p["id"],q,p["precio_venta"]));c.execute("UPDATE inventario SET stock=stock-? WHERE id=?",(q,p["id"]))
            c.commit();self.invoice(vid,cid,total);messagebox.showinfo("Venta",f"Venta #{vid} registrada y facturada.")
            self.clear_cart();self.refresh_options();self.app.refresh_dashboard()
        except Exception as e:c.rollback();error(str(e))
        finally:c.close()
    def invoice(self,vid,cid,total):
        c=get_connection();rows=c.execute("SELECT vd.cantidad,vd.precio,i.codigo,i.nombre FROM venta_detalle vd JOIN inventario i ON i.id=vd.producto_id WHERE vd.venta_id=?",(vid,)).fetchall();c.close()
        cliente="Consumidor final"
        if cid:
            c=get_connection();r=c.execute("SELECT nombre FROM clientes WHERE id=?",(cid,)).fetchone();c.close();cliente=r["nombre"] if r else cliente
        Path("facturas").mkdir(exist_ok=True);p=Path("facturas")/f"factura_{vid}.txt"
        with open(p,"w",encoding="utf-8") as f:
            f.write("SISTEMA DE VENTAS ERP\nFACTURA DE VENTA\n"+"="*40+"\n");f.write(f"Factura: {vid}\nCliente: {cliente}\n\n")
            for r in rows:f.write(f'{r["codigo"]} - {r["nombre"]} x{r["cantidad"]} = {money(float(r["precio"])*r["cantidad"])}\n')
            f.write("="*40+f"\nTOTAL: {money(total)}\n")
    def clear_cart(self):self.cart=[];self.render()
