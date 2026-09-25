import sqlite3, hashlib
from pathlib import Path
from config import DB_NAME,DB_BACKEND,MYSQL_HOST,MYSQL_PORT,MYSQL_USER,MYSQL_PASSWORD,MYSQL_DATABASE
DB_PATH=Path(__file__).resolve().parent/DB_NAME
_ACTIVE_BACKEND="sqlite"
class RowDict(dict):
    def __getitem__(self,k): return list(self.values())[k] if isinstance(k,int) else super().__getitem__(k)
class CursorAdapter:
    def __init__(self,cursor,rows): self.cursor=cursor; self.rows=rows
    def fetchone(self): return self.rows.pop(0) if self.rows else None
    def fetchall(self): r=self.rows; self.rows=[]; return r
    @property
    def lastrowid(self): return self.cursor.lastrowid
class DBConnection:
    def __init__(self,c,b): self.conn=c; self.backend=b
    def execute(self,sql,p=()):
        if self.backend=="mysql":
            cur=self.conn.cursor(dictionary=True); cur.execute(sql.replace("?","%s"),tuple(p)); rows=[RowDict(x) for x in cur.fetchall()] if cur.description else []
            return CursorAdapter(cur,rows)
        cur=self.conn.execute(sql,p); return CursorAdapter(cur,[RowDict(dict(x)) for x in cur.fetchall()] if cur.description else [])
    def executemany(self,sql,seq):
        if self.backend=="mysql": cur=self.conn.cursor(); cur.executemany(sql.replace("?","%s"),seq); return CursorAdapter(cur,[])
        return CursorAdapter(self.conn.executemany(sql,seq),[])
    def commit(self): self.conn.commit()
    def rollback(self): self.conn.rollback()
    def close(self): self.conn.close()
def _mysql():
    import mysql.connector
    return DBConnection(mysql.connector.connect(host=MYSQL_HOST,port=MYSQL_PORT,user=MYSQL_USER,password=MYSQL_PASSWORD,database=MYSQL_DATABASE),"mysql")
def get_connection():
    global _ACTIVE_BACKEND
    if DB_BACKEND.lower()=="mysql":
        try: c=_mysql(); _ACTIVE_BACKEND="mysql"; return c
        except Exception: pass
    c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row; c.execute("PRAGMA foreign_keys=ON"); _ACTIVE_BACKEND="sqlite"; return DBConnection(c,"sqlite")
def backend_name(): return _ACTIVE_BACKEND
SCHEMA_SQLITE="""CREATE TABLE IF NOT EXISTS usuarios(id INTEGER PRIMARY KEY AUTOINCREMENT,usuario TEXT UNIQUE NOT NULL,password_hash TEXT NOT NULL,rol TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS clientes(id INTEGER PRIMARY KEY AUTOINCREMENT,nombre TEXT NOT NULL,documento TEXT,telefono TEXT,email TEXT,direccion TEXT);
CREATE TABLE IF NOT EXISTS proveedores(id INTEGER PRIMARY KEY AUTOINCREMENT,nombre TEXT NOT NULL,documento TEXT,telefono TEXT,email TEXT,direccion TEXT);
CREATE TABLE IF NOT EXISTS inventario(id INTEGER PRIMARY KEY AUTOINCREMENT,codigo TEXT UNIQUE NOT NULL,nombre TEXT NOT NULL,categoria TEXT,precio_compra REAL DEFAULT 0,precio_venta REAL DEFAULT 0,stock INTEGER DEFAULT 0,stock_minimo INTEGER DEFAULT 5);
CREATE TABLE IF NOT EXISTS compras(id INTEGER PRIMARY KEY AUTOINCREMENT,proveedor_id INTEGER,fecha TEXT DEFAULT CURRENT_TIMESTAMP,total REAL DEFAULT 0,FOREIGN KEY(proveedor_id) REFERENCES proveedores(id) ON DELETE SET NULL);
CREATE TABLE IF NOT EXISTS compra_detalle(id INTEGER PRIMARY KEY AUTOINCREMENT,compra_id INTEGER,producto_id INTEGER,cantidad INTEGER,precio REAL,FOREIGN KEY(compra_id) REFERENCES compras(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS ventas(id INTEGER PRIMARY KEY AUTOINCREMENT,cliente_id INTEGER,fecha TEXT DEFAULT CURRENT_TIMESTAMP,total REAL DEFAULT 0,FOREIGN KEY(cliente_id) REFERENCES clientes(id) ON DELETE SET NULL);
CREATE TABLE IF NOT EXISTS venta_detalle(id INTEGER PRIMARY KEY AUTOINCREMENT,venta_id INTEGER,producto_id INTEGER,cantidad INTEGER,precio REAL,FOREIGN KEY(venta_id) REFERENCES ventas(id) ON DELETE CASCADE);"""
SCHEMA_MYSQL=[
"CREATE TABLE IF NOT EXISTS usuarios(id INT AUTO_INCREMENT PRIMARY KEY,usuario VARCHAR(80) UNIQUE NOT NULL,password_hash VARCHAR(128) NOT NULL,rol VARCHAR(30) NOT NULL)",
"CREATE TABLE IF NOT EXISTS clientes(id INT AUTO_INCREMENT PRIMARY KEY,nombre VARCHAR(150) NOT NULL,documento VARCHAR(50),telefono VARCHAR(50),email VARCHAR(150),direccion VARCHAR(200))",
"CREATE TABLE IF NOT EXISTS proveedores(id INT AUTO_INCREMENT PRIMARY KEY,nombre VARCHAR(150) NOT NULL,documento VARCHAR(50),telefono VARCHAR(50),email VARCHAR(150),direccion VARCHAR(200))",
"CREATE TABLE IF NOT EXISTS inventario(id INT AUTO_INCREMENT PRIMARY KEY,codigo VARCHAR(50) UNIQUE NOT NULL,nombre VARCHAR(150) NOT NULL,categoria VARCHAR(100),precio_compra DECIMAL(12,2) DEFAULT 0,precio_venta DECIMAL(12,2) DEFAULT 0,stock INT DEFAULT 0,stock_minimo INT DEFAULT 5)",
"CREATE TABLE IF NOT EXISTS compras(id INT AUTO_INCREMENT PRIMARY KEY,proveedor_id INT NULL,fecha DATETIME DEFAULT CURRENT_TIMESTAMP,total DECIMAL(12,2) DEFAULT 0,FOREIGN KEY(proveedor_id) REFERENCES proveedores(id) ON DELETE SET NULL)",
"CREATE TABLE IF NOT EXISTS compra_detalle(id INT AUTO_INCREMENT PRIMARY KEY,compra_id INT,producto_id INT,cantidad INT,precio DECIMAL(12,2),FOREIGN KEY(compra_id) REFERENCES compras(id) ON DELETE CASCADE)",
"CREATE TABLE IF NOT EXISTS ventas(id INT AUTO_INCREMENT PRIMARY KEY,cliente_id INT NULL,fecha DATETIME DEFAULT CURRENT_TIMESTAMP,total DECIMAL(12,2) DEFAULT 0,FOREIGN KEY(cliente_id) REFERENCES clientes(id) ON DELETE SET NULL)",
"CREATE TABLE IF NOT EXISTS venta_detalle(id INT AUTO_INCREMENT PRIMARY KEY,venta_id INT,producto_id INT,cantidad INT,precio DECIMAL(12,2),FOREIGN KEY(venta_id) REFERENCES ventas(id) ON DELETE CASCADE)"
]
def _seed(c):
    h=lambda p:hashlib.sha256(p.encode()).hexdigest()
    if c.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]==0:c.executemany("INSERT INTO usuarios(usuario,password_hash,rol) VALUES(?,?,?)",[("admin",h("admin123"),"Administrador"),("gerente",h("gerente123"),"Gerente"),("vendedor",h("vendedor123"),"Vendedor")])
    if c.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]==0:c.executemany("INSERT INTO clientes(nombre,documento,telefono,email,direccion) VALUES(?,?,?,?,?)",[("Carlos Pérez","1001001001","3001112233","carlos@email.com","Barranquilla"),("María Gómez","1002002002","3012223344","maria@email.com","Soledad")])
    if c.execute("SELECT COUNT(*) FROM proveedores").fetchone()[0]==0:c.executemany("INSERT INTO proveedores(nombre,documento,telefono,email,direccion) VALUES(?,?,?,?,?)",[("Distribuciones Caribe","900111222","6055551111","ventas@caribe.com","Barranquilla"),("Comercial La 72","900333444","6055552222","contacto@la72.com","Barranquilla")])
    if c.execute("SELECT COUNT(*) FROM inventario").fetchone()[0]==0:c.executemany("INSERT INTO inventario(codigo,nombre,categoria,precio_compra,precio_venta,stock,stock_minimo) VALUES(?,?,?,?,?,?,?)",[("P001","Cuaderno ecológico","Papelería",5000,8000,35,5),("P002","Agenda personalizada","Papelería",9000,15000,18,5),("P003","Póster creativo","Diseño",3500,7000,12,3),("P004","Carpeta kraft","Papelería",2500,5000,25,5)])
def init_db():
    if DB_BACKEND.lower()=="mysql":
        try:
            import mysql.connector
            raw=mysql.connector.connect(host=MYSQL_HOST,port=MYSQL_PORT,user=MYSQL_USER,password=MYSQL_PASSWORD)
            cur=raw.cursor(); cur.execute(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DATABASE}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"); raw.commit(); cur.close(); raw.close()
            c=_mysql()
            for s in SCHEMA_MYSQL:c.execute(s)
            _seed(c); c.commit(); c.close(); return
        except Exception: pass
    c=get_connection(); c.conn.executescript(SCHEMA_SQLITE); _seed(c); c.commit(); c.close()
def authenticate(u,p):
    c=get_connection(); r=c.execute("SELECT * FROM usuarios WHERE usuario=?",(u,)).fetchone(); c.close()
    return {"id":r["id"],"usuario":r["usuario"],"rol":r["rol"]} if r and hashlib.sha256(p.encode()).hexdigest()==r["password_hash"] else None
