from flask import Flask, render_template, request, jsonify, redirect, session
import mysql.connector
import json
import os
app = Flask(__name__)

db_conf = {
    "host": os.getenv("mysql-a5b4356-hazielmoyacruz-33df.l.aivencloud.com"),
    "port": int(os.getenv(19103)),
    "user": os.getenv("avnadmin"),
    "password": os.getenv("AVNS_KCvM9coBZ6aL7GMQ6sX"),
    "database": os.getenv("inventario")
}
def conexion():
    return mysql.connector.connect(**db_conf)
# LOGIN
@app.route("/")
def login():
    return render_template("login2.html")
# VALIDAR LOGIN
@app.route("/login2", methods=["POST"])
def validar_login():
    correo = request.form.get("correo")
    password = request.form.get("password")

    con = conexion()
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM personal WHERE correo=%s AND contrasena=%s", (correo, password))
    usuario = cursor.fetchone()
    cursor.close()
    con.close()

    if usuario:
        session["usuario"] = usuario  # guarda todo el dict del usuario
        return redirect("/inventario2")
    else:
        return render_template("login2.html", error="Correo o contraseña incorrectos")


@app.route("/cuenta")
def cuenta():
    usuario = session.get("usuario")
    if not usuario:
        return redirect("/")
    return render_template("cuenta.html", usuario=usuario)


# REGISTRO
@app.route("/registro2")
def registro():
    return render_template("registro2.html")
# GUARDAR USUARIO
@app.route("/guardar_usuario2", methods=["POST"])
def guardar_usuario():
    nombre = request.form["nombre"]
    apellido_p = request.form["apellido_p"]
    apellido_m = request.form["apellido_m"]
    telefono = request.form["telefono"]
    correo = request.form["correo"]
    contrasena = request.form["password"]
    con = conexion()
    cursor = con.cursor()
    sql = """
    INSERT INTO personal
    (nombre, apellido_p, apellido_m, telefono, correo, contrasena)
    VALUES(%s,%s,%s,%s,%s,%s)
    """
    cursor.execute(sql, (nombre, apellido_p, apellido_m, telefono, correo, contrasena))
    con.commit()
    cursor.close()
    con.close()
    return redirect("/")
@app.route("/logout2")
def logout():
    session.pop("usuario", None)
    return redirect("/")
# INVENTARIO
@app.route("/inventario2")
def inventario():
    usuario = session.get("usuario")
    if not usuario:
        return redirect("/")  # si no hay sesión, vuelve al login
    con = conexion()
    cursor = con.cursor(dictionary=True)
    # Productos
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    # Proveedores
    cursor.execute("SELECT * FROM proveedores")
    proveedores = cursor.fetchall()
    # Estadísticas
    cursor.execute("SELECT COUNT(*) AS total_registros FROM productos")
    total_registros = cursor.fetchone()["total_registros"]
    cursor.execute("SELECT SUM(total) AS total_ventas FROM ventas")
    total_ventas = cursor.fetchone()["total_ventas"]
    cursor.execute("SELECT SUM(cantidad) AS productos_vendidos FROM detalle_venta")
    productos_vendidos = cursor.fetchone()["productos_vendidos"]
    cursor.close()
    con.close()
    return render_template(
        "inventario2.html",
        usuario=usuario,
        productos=productos,
        proveedores=proveedores,
        total_registros=total_registros,
        total_ventas=total_ventas,
        productos_vendidos=productos_vendidos
    )

# PRODUCTOS CRUD
@app.route("/productos2")
def productos():
    con = conexion()
    cursor = con.cursor(dictionary=True)
    sql = """
    SELECT productos.*, proveedores.nombre AS proveedor
    FROM productos
    LEFT JOIN proveedores ON productos.id_proveedor = proveedores.id_proveedor
    """
    cursor.execute(sql)
    productos = cursor.fetchall()
    cursor.close()
    con.close()
    return render_template("productos2.html", productos=productos)

@app.route("/nuevo_producto2")
def nuevo_producto2():
    con = conexion()
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM proveedores")
    proveedores = cursor.fetchall()
    cursor.close()
    con.close()
    # 🔹 Aquí cambias el nombre de la plantilla
    return render_template("producto_form2.html", proveedores=proveedores)


@app.route("/guardar_producto2", methods=["POST"])
def guardar_producto2():
    clave = request.form["clave"]
    nombre = request.form["nombre"]
    stock = request.form["stock"]
    contenido = request.form["contenido"]
    precio = request.form["precio"]
    proveedor = request.form["proveedor"]

    con = conexion()
    cursor = con.cursor()
    sql = "INSERT INTO productos (clave, nombre, stock, contenido, precio, id_proveedor) VALUES (%s,%s,%s,%s,%s,%s)"
    cursor.execute(sql, (clave, nombre, stock, contenido, precio, proveedor))
    con.commit()
    cursor.close()
    con.close()
    return redirect("/inventario2")

@app.route("/editar_producto2/<int:clave>")
def editar_producto(clave):
    con = conexion()
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos WHERE clave = %s", (clave,))
    producto = cursor.fetchone()
    cursor.execute("SELECT * FROM proveedores")
    proveedores = cursor.fetchall()
    cursor.close()
    con.close()
    return render_template("editar_producto2.html", producto=producto, proveedores=proveedores)

@app.route("/actualizar_producto2", methods=["POST"])
def actualizar_producto2():
    clave = request.form["clave"]
    nombre = request.form["nombre"]
    stock = request.form["stock"]
    contenido = request.form["contenido"]
    precio = request.form["precio"]
    proveedor = request.form["proveedor"]
    con = conexion()
    cursor = con.cursor()
    sql = """
    UPDATE productos
    SET nombre=%s, stock=%s, contenido=%s, precio=%s, id_proveedor=%s
    WHERE clave=%s
    """
    cursor.execute(sql, (nombre, stock, contenido, precio, proveedor, clave))
    con.commit()
    cursor.close()
    con.close()
    # 🔹 Aquí rediriges a inventario2
    return redirect("/inventario2")

@app.route("/eliminar_producto2/<int:clave>")
def eliminar_producto2(clave):
    con = conexion()
    cursor = con.cursor()
    cursor.execute("DELETE FROM productos WHERE clave=%s", (clave,))
    con.commit()
    cursor.close()
    con.close()
    return redirect("/inventario2")

# PROVEEDORES CRUD
@app.route("/proveedores2")
def proveedores():
    con = conexion()
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM proveedores")
    proveedores = cursor.fetchall()
    cursor.close()
    con.close()
    return render_template("proveedores2.html", proveedores=proveedores)

@app.route("/proveedor_form2")
def proveedor_form():
    return render_template("proveedor_form2.html")

@app.route("/guardar_proveedor2", methods=["POST"])
def guardar_proveedor():
    nombre = request.form["nombre"]
    numero = request.form["numero"]
    direccion = request.form["direccion"]
    tipo_proveedor = request.form["tipo_proveedor"]
    correo = request.form["correo"]
    con = conexion()
    cursor = con.cursor()
    sql = """
    INSERT INTO proveedores (nombre, numero, direccion, tipo_proveedor, correo)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (nombre, numero, direccion, tipo_proveedor, correo))
    con.commit()
    cursor.close()
    con.close()
    return redirect("/proveedores2")

@app.route("/editar_proveedor2/<int:id>")
def editar_proveedor(id):
    con = conexion()
    cursor = con.cursor(dictionary=True)
    sql = "SELECT * FROM proveedores WHERE id_proveedor = %s"
    cursor.execute(sql, (id,))
    proveedor = cursor.fetchone()
    cursor.close()
    con.close()
    return render_template("editar_proveedor2.html", proveedor=proveedor)

@app.route("/actualizar_proveedor2", methods=["POST"])
def actualizar_proveedor():
    id_proveedor = request.form["id_proveedor"]
    nombre = request.form["nombre"]
    numero = request.form["numero"]
    direccion = request.form["direccion"]
    tipo_proveedor = request.form["tipo_proveedor"]
    correo = request.form["correo"]
    con = conexion()
    cursor = con.cursor()
    sql = """
    UPDATE proveedores
    SET nombre=%s, numero=%s, direccion=%s, tipo_proveedor=%s, correo=%s
    WHERE id_proveedor=%s
    """
    cursor.execute(sql, (nombre, numero, direccion, tipo_proveedor, correo, id_proveedor))
    con.commit()
    cursor.close()
    con.close()
    return redirect("/proveedores2")

@app.route("/eliminar_proveedor2/<int:id_proveedor>")
def eliminar_proveedor(id_proveedor):
    con = conexion()
    cursor = con.cursor()
    sql = "DELETE FROM proveedores WHERE id_proveedor = %s"
    cursor.execute(sql, (id_proveedor,))
    con.commit()
    cursor.close()
    con.close()
    return redirect("/proveedores2")

# VENTAS
@app.route("/ventas2")
def ventas():
    con = conexion()
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    cursor.close()
    con.close()
    productos_dict = {p["clave"]: p["precio"] for p in productos}
    productos_json = json.dumps(productos_dict)
    return render_template("venta_form2.html", productos=productos, productos_json=productos_json)


# Buscar producto por clave (AJAX)
@app.route("/buscar_producto2", methods=["POST"])
def buscar_producto2():
    data = request.get_json()
    codigo = data.get("codigo", "").upper()
    con = conexion()
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos WHERE clave = %s", (codigo,))
    producto = cursor.fetchone()
    cursor.close()
    con.close()
    if producto:
        return jsonify({"success": True, "producto": producto})
    return jsonify({"success": False, "mensaje": "Producto no encontrado"})


from datetime import datetime

@app.route("/guardar_compra2", methods=["POST"])
def guardar_compra2():
    fecha = request.form["fecha"]
    productos = request.form.getlist("producto[]")
    cantidades = request.form.getlist("cantidad[]")
    pago = float(request.form["pago"])
    usuario = session.get("usuario")

    con = conexion()
    cursor = con.cursor(dictionary=True)

    total = 0
    subtotales = []

    # calcular subtotales y validar stock
    for i in range(len(productos)):
        cursor.execute("SELECT precio, stock FROM productos WHERE clave = %s", (productos[i],))
        producto = cursor.fetchone()
        if producto:
            precio = producto["precio"]
            stock_actual = producto["stock"]
            cantidad = int(cantidades[i])

            # validar stock
            if cantidad > stock_actual:
                cursor.close()
                con.close()
                return f"<script>alert('⚠️ No hay suficiente stock para el producto {productos[i]}. Stock disponible: {stock_actual}'); window.location.href='/ventas2';</script>"

            subtotal = precio * cantidad
            subtotales.append(subtotal)
            total += subtotal

    # validar pago
    if pago < total:
        cursor.close()
        con.close()
        return "<script>alert('⚠️ Pago insuficiente. Debe cubrir al menos el total.'); window.location.href='/ventas2';</script>"

    # insertar en transacciones
    hora = datetime.now().strftime("%H:%M:%S")
    cursor = con.cursor()
    cursor.execute("""
        INSERT INTO transacciones (fecha, hora, total, id_personal)
        VALUES (%s, %s, %s, %s)
    """, (fecha, hora, total, usuario["id_personal"]))
    id_transaccion = cursor.lastrowid

    # insertar detalle_venta y actualizar stock
    for i in range(len(productos)):
        cursor.execute("""
            INSERT INTO detalle_venta (id_transaccion, clave_producto, cantidad, subtotal)
            VALUES (%s, %s, %s, %s)
        """, (id_transaccion, productos[i], cantidades[i], subtotales[i]))

        cursor.execute("""
            UPDATE productos SET stock = stock - %s WHERE clave = %s
        """, (cantidades[i], productos[i]))

    con.commit()
    cursor.close()
    con.close()

    cambio = pago - total
    return f"<script>alert('✅ Compra registrada. Cambio: ${cambio:.2f}'); window.location.href='/inventario2';</script>"

@app.route("/registro_ventas2")
def registro_ventas2():
    con = conexion()
    cursor = con.cursor(dictionary=True)
    # Traemos las transacciones junto con el nombre del usuario
    cursor.execute("""
        SELECT t.id_transaccion, t.fecha, t.hora, t.total, p.nombre AS usuario
        FROM transacciones t
        INNER JOIN personal p ON t.id_personal = p.id_personal
        ORDER BY t.fecha DESC, t.hora DESC
    """)
    ventas = cursor.fetchall()
    cursor.close()
    con.close()
    return render_template("registro_ventas2.html", ventas=ventas)

# ESTADÍSTICAS
@app.route("/estadisticas2")
def estadisticas2():
    con = conexion()
    cursor = con.cursor(dictionary=True)
    # Total de ventas registradas
    cursor.execute("SELECT COUNT(*) AS total_ventas FROM transacciones")
    total_ventas = cursor.fetchone()["total_ventas"]
    # Suma total de ingresos
    cursor.execute("SELECT SUM(total) AS ingresos FROM transacciones")
    ingresos = cursor.fetchone()["ingresos"] or 0
    # Producto más vendido
    cursor.execute("""
        SELECT p.nombre, SUM(d.cantidad) AS cantidad
        FROM detalle_venta d
        INNER JOIN productos p ON d.clave_producto = p.clave
        GROUP BY p.nombre
        ORDER BY cantidad DESC
        LIMIT 1
    """)
    producto_top = cursor.fetchone()
    cursor.close()
    con.close()
    return render_template("estadisticas2.html",
                           total_ventas=total_ventas,
                           ingresos=ingresos,
                           producto_top=producto_top)

# BUSCAR PRODUCTO (AJAX)
@app.route("/buscar_producto2", methods=["POST"])
def buscar_producto():
    data = request.get_json()
    codigo = data.get("codigo", "").upper()
    con = conexion()
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos WHERE clave = %s", (codigo,))
    producto = cursor.fetchone()
    cursor.close()
    con.close()
    if producto:
        return jsonify({"success": True, "producto": producto})
    return jsonify({"success": False, "mensaje": "Producto no encontrado"})

if __name__ == "__main__":
    app.run(debug=True)
