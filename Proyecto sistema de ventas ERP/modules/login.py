import tkinter as tk
from tkinter import ttk,messagebox
from database import authenticate
class LoginFrame(tk.Toplevel):
    def __init__(self,parent,on_success):
        super().__init__(parent); self.on_success=on_success
        self.title("ERP V3 - Iniciar sesión"); self.geometry("430x300"); self.resizable(False,False); self.grab_set()
        ttk.Label(self,text="ERP V3",font=("Segoe UI",24,"bold")).pack(pady=(25,2))
        ttk.Label(self,text="Inicio de sesión").pack(pady=(0,20))
        f=ttk.Frame(self); f.pack(); self.user=tk.StringVar(); self.password=tk.StringVar()
        ttk.Label(f,text="Usuario").grid(row=0,column=0,padx=8,pady=8); ttk.Entry(f,textvariable=self.user,width=28).grid(row=0,column=1)
        ttk.Label(f,text="Contraseña").grid(row=1,column=0,padx=8,pady=8); ttk.Entry(f,textvariable=self.password,show="*",width=28).grid(row=1,column=1)
        ttk.Button(self,text="Iniciar sesión",command=self.login).pack(pady=20)
        ttk.Label(self,text="Demo: admin/admin123 · gerente/gerente123 · vendedor/vendedor123",font=("Segoe UI",8)).pack()
        self.protocol("WM_DELETE_WINDOW",parent.destroy)
    def login(self):
        d=authenticate(self.user.get().strip(),self.password.get())
        if not d: messagebox.showerror("Acceso","Usuario o contraseña incorrectos."); return
        self.destroy(); self.on_success(d)
