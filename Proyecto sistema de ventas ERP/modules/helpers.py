import tkinter as tk
from tkinter import ttk, messagebox

def money(value):
    return f"${value:,.0f}".replace(",", ".")

def clear_tree(tree):
    for item in tree.get_children():
        tree.delete(item)

def make_tree(parent, columns, widths=None):
    tree = ttk.Treeview(parent, columns=columns, show="headings")
    widths = widths or [120] * len(columns)
    for col, width in zip(columns, widths):
        tree.heading(col, text=col)
        tree.column(col, width=width, anchor="w")
    scroll = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scroll.set)
    tree.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")
    return tree

def confirm(msg):
    return messagebox.askyesno("Confirmar", msg)

def info(msg):
    messagebox.showinfo("ERP", msg)

def error(msg):
    messagebox.showerror("Error", msg)
