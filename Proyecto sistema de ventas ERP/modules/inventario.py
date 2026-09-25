import tkinter as tk
from tkinter import ttk
from database import get_connection
from modules.helpers import make_tree,clear_tree,confirm,error,info,money
class InventarioFrame(ttk.Frame):
    def __init__(self,parent,app):
        super().__init__(parent); self.app=app; self.edit_id=None; self.build(); self.load()
    def build(self):
        form=ttk.LabelFrame(self,text="Producto"); form.pack(fill="x",padx=12,pady=12)
        keys=["codigo","nombre","categoria","precio_compra","precio_venta","stock","stock_minimo"]; self.vars={k:tk.StringVar() for k in keys}
        for i,k in enumerate(keys):ttk.Label(form,text=k.replace("_"," ").title()).grid(row=0,column=i*2,padx=4,pady=5); ttk.Entry(form,textvariable=self.vars[k],width=14).grid(row=0,column=i*2+1,padx=4,pady=5)
        ttk.Button(form,text="Guardar / Actualizar",command=self.save).grid(row=1,column=0,padx=4,pady=6); ttk.Button(form,text="Limpiar",command=self.clear).grid(row=1,column=1,padx=4,pady=6); ttk.Button(form,text="Eliminar",command=self.delete).grid(row=1,column=2,padx=4,pady=6)
        s=ttk.Frame(self); s.pack(fill="x",padx=12,pady=(0,8)); ttk.Label(s,text="Buscar:").pack(side="left"); self.q=tk.StringVar(); ttk.Entry(s,textvariable=self.q,width=35).pack(side="left",padx=6); ttk.Button(s,text="Buscar",command=self.load).pack(side="left")
        self.tree=make_tree(self,["ID","Código","Producto","Categoría","Compra","Venta","Stock","Mínimo"],[50,90,190,120,100,100,80,80]); self.tree.bind("<<TreeviewSelect>>",self.select)
    def load(self):
        clear_tree(self.tree); q=self.q.get().strip(); c=get_connection(); rows=c.execute("SELECT * FROM inventario WHERE codigo LIKE ? OR nombre LIKE ? OR categoria LIKE ? ORDER BY id DESC",(f"%{q}%",f"%{q}%",f"%{q}%")).fetchall(); c.close()
        for r in rows:self.tree.insert("","end",values=(r["id"],r["codigo"],r["nombre"],r["categoria"],money(r["precio_compra"]),money(r["precio_venta"]),r["stock"],r["stock_minimo"]))
    def save(self):
        try:
            v={k:self.vars[k].get().strip() for k in self.vars}
            if not v["codigo"] or not v["nombre"]:raise ValueError("Código y nombre son obligatorios.")
            c=get_connection()
            if self.edit_id:c.execute("UPDATE inventario SET codigo=?,nombre=?,categoria=?,precio_compra=?,precio_venta=?,stock=?,stock_minimo=? WHERE id=?",(v["codigo"],v["nombre"],v["categoria"],float(v["precio_compra"] or 0),float(v["precio_venta"] or 0),int(v["stock"] or 0),int(v["stock_minimo"] or 5),self.edit_id))
            else:c.execute("INSERT INTO inventario(codigo,nombre,categoria,precio_compra,precio_venta,stock,stock_minimo) VALUES(?,?,?,?,?,?,?)",(v["codigo"],v["nombre"],v["categoria"],float(v["precio_compra"] or 0),float(v["precio_venta"] or 0),int(v["stock"] or 0),int(v["stock_minimo"] or 5)))
            c.commit();c.close();info("Producto guardado correctamente.");self.clear();self.load();self.app.refresh_dashboard()
        except Exception as e:error("No se pudo guardar. Revisa los datos.\n"+str(e))
    def select(self,_=None):
        s=self.tree.selection()
        if not s:return
        id_=self.tree.item(s[0],"values")[0]; c=get_connection(); r=c.execute("SELECT * FROM inventario WHERE id=?",(id_,)).fetchone(); c.close(); self.edit_id=id_
        for k in self.vars:self.vars[k].set(r[k])
    def delete(self):
        s=self.tree.selection()
        if not s:return
        if not confirm("¿Eliminar el producto seleccionado?"):return
        c=get_connection(); 
        try:c.execute("DELETE FROM inventario WHERE id=?",(self.tree.item(s[0],"values")[0],));c.commit();self.clear();self.load()
        except Exception as e:c.rollback();error("No se puede eliminar si el producto tiene movimientos asociados.\n"+str(e))
        finally:c.close()
    def clear(self):
        self.edit_id=None
        for v in self.vars.values():v.set("")
