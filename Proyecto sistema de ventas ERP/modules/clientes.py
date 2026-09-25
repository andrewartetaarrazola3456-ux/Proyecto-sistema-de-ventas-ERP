import tkinter as tk
from tkinter import ttk
from database import get_connection
from modules.helpers import make_tree,clear_tree,confirm,error,info
class ClientesFrame(ttk.Frame):
    def __init__(self,parent,app):
        super().__init__(parent); self.app=app; self.edit_id=None; self.build(); self.load()
    def build(self):
        form=ttk.LabelFrame(self,text="Datos del cliente");form.pack(fill="x",padx=12,pady=12)
        self.vars={k:tk.StringVar() for k in ["nombre","documento","telefono","email","direccion"]}
        for i,(label,key) in enumerate([("Nombre","nombre"),("Documento","documento"),("Teléfono","telefono"),("Email","email"),("Dirección","direccion")]):
            ttk.Label(form,text=label).grid(row=0,column=i*2,padx=5,pady=8);ttk.Entry(form,textvariable=self.vars[key],width=20).grid(row=0,column=i*2+1,padx=5,pady=8)
        ttk.Button(form,text="Guardar / Actualizar",command=self.save).grid(row=1,column=0,padx=5,pady=8);ttk.Button(form,text="Limpiar",command=self.clear).grid(row=1,column=1,padx=5,pady=8);ttk.Button(form,text="Eliminar seleccionado",command=self.delete).grid(row=1,column=2,padx=5,pady=8)
        s=ttk.Frame(self);s.pack(fill="x",padx=12,pady=(0,8));ttk.Label(s,text="Buscar:").pack(side="left");self.q=tk.StringVar();ttk.Entry(s,textvariable=self.q,width=35).pack(side="left",padx=6);ttk.Button(s,text="Buscar",command=self.load).pack(side="left")
        self.tree=make_tree(self,["ID","Nombre","Documento","Teléfono","Email","Dirección"],[60,180,120,120,220,180]);self.tree.bind("<<TreeviewSelect>>",self.select)
    def load(self):
        clear_tree(self.tree);q=self.q.get().strip();c=get_connection();rows=c.execute("SELECT * FROM clientes WHERE nombre LIKE ? OR documento LIKE ? OR telefono LIKE ? ORDER BY id DESC",(f"%{q}%",f"%{q}%",f"%{q}%")).fetchall();c.close()
        for r in rows:self.tree.insert("","end",values=tuple(r[k] for k in ["id","nombre","documento","telefono","email","direccion"]))
    def save(self):
        if not self.vars["nombre"].get().strip():error("El nombre es obligatorio.");return
        c=get_connection();v=tuple(self.vars[k].get().strip() for k in self.vars)
        try:
            if self.edit_id:c.execute("UPDATE clientes SET nombre=?,documento=?,telefono=?,email=?,direccion=? WHERE id=?",v+(self.edit_id,))
            else:c.execute("INSERT INTO clientes(nombre,documento,telefono,email,direccion) VALUES(?,?,?,?,?)",v)
            c.commit();info("Cliente guardado correctamente.");self.clear();self.load();self.app.refresh_dashboard()
        except Exception as e:c.rollback();error(str(e))
        finally:c.close()
    def select(self,_=None):
        s=self.tree.selection()
        if not s:return
        v=self.tree.item(s[0],"values");self.edit_id=v[0]
        for k,x in zip(self.vars,v[1:]):self.vars[k].set(x)
    def delete(self):
        s=self.tree.selection()
        if not s:return
        if not confirm("¿Eliminar el cliente seleccionado?"):return
        c=get_connection();c.execute("DELETE FROM clientes WHERE id=?",(self.tree.item(s[0],"values")[0],));c.commit();c.close();self.clear();self.load()
    def clear(self):
        self.edit_id=None
        for v in self.vars.values():v.set("")
