# Proyecto Sistema de Ventas ERP

## Ejecución
1. Instalar Python 3.10 o superior.
2. Para MySQL instalar: `pip install mysql-connector-python`
3. Editar `config.py` con las credenciales de MySQL.
4. Ejecutar `python main.py`.

El sistema intenta MySQL primero. Si MySQL no está disponible, utiliza SQLite local.

### Usuarios demo
- admin / admin123
- gerente / gerente123
- vendedor / vendedor123

### MySQL Workbench
Ejecutar `sistema_ventas_erp_mysql.sql` o dejar que `database.py` cree la base automáticamente.

## Módulos
Dashboard, Clientes, Proveedores, Inventario, Ventas, Compras, Reportes, Login y Facturación.

## Entrega
El DOCX incluido está organizado en APA 7 e incluye espacios para capturas del MER, casos de uso, Dashboard, módulos, evidencias funcionales y evidencias técnicas.
