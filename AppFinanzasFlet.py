import flet as ft
import sqlite3
import re
from datetime import datetime

DB_NAME = r"G:\Mi unidad\DBSqllite\DBAppFinanzasFlet.db"

# ---------- BASE DE DATOS ---------- 12/02/2026 18:43
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tab_registros (
            tab_reg_id INTEGER PRIMARY KEY AUTOINCREMENT,
            tab_reg_tipo TEXT,
            tab_reg_monto INTEGER,
            tab_reg_cuenta TEXT,
            tab_reg_categoria TEXT,
            tab_reg_descripcion TEXT,
            tab_reg_fecha TEXT
        )
    """)
    conn.commit()
    conn.close()


def insertar_registro(data):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO tab_registros 
        (tab_reg_tipo,tab_reg_monto,tab_reg_cuenta,tab_reg_categoria,tab_reg_descripcion,tab_reg_fecha)
        VALUES (?,?,?,?,?,?)
    """, data)
    conn.commit()
    conn.close()


def obtener_ultimos():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT * FROM tab_registros ORDER BY tab_reg_id DESC LIMIT 5")
    rows = cur.fetchall()
    conn.close()
    return rows


def eliminar_registro(rid):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("DELETE FROM tab_registros WHERE tab_reg_id=?", (rid,))
    conn.commit()
    conn.close()


def actualizar_registro(data):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        UPDATE tab_registros
        SET tab_reg_tipo=?, tab_reg_monto=?, tab_reg_cuenta=?, tab_reg_categoria=?, tab_reg_descripcion=?, tab_reg_fecha=?
        WHERE tab_reg_id=?
    """, data)
    conn.commit()
    conn.close()

# ---------- APP ----------

def main(page: ft.Page):

    init_db()

    page.title = "Control Finanzas"
    page.scroll = ft.ScrollMode.AUTO

    editando_id = {"id": None}
    borrar_id = {"id": None}

    # ---------- FUNCIONES ----------

    def mostrar_mensaje(msg):
        page.snack_bar = ft.SnackBar(ft.Text(msg))
        page.snack_bar.open = True
        page.update()

    def formato_miles(valor):
        return f"{int(valor):,}".replace(",", ".")

    def formato_fecha(valor):
        return re.sub(r"(\d{2})(\d{2})(\d{4})", r"\1/\2/\3", valor)

    def confirmar_borrar():
        if boton_confirmar.on_click:
            eliminar_registro(borrar_id["id"])
            cargar_tabla()
            mostrar_mensaje("Registro eliminado")

    # ---------- VALIDACIONES ----------
    def validar_descripcion(txt):
        return bool(re.fullmatch(r"[A-Z0-9.,+\- ]+", txt))

    # ---------- GUARDAR ----------
    def guardar_registro(e):

        monto = re.sub(r"\D", "", input_monto.value)

        if not monto:
            mostrar_mensaje("Monto inválido")
            return

        if not input_descripcion.value.strip():
            mostrar_mensaje("Descripción obligatoria")
            return

        if not validar_descripcion(input_descripcion.value):
            mostrar_mensaje("Descripción inválida")
            return

        if not input_fecha.value:
            mostrar_mensaje("Seleccione fecha")
            return

        data = (
            input_tipo.value,
            int(monto),
            input_cuenta.value,
            input_categoria.value,
            input_descripcion.value,
            input_fecha.value,
        )

        if editando_id["id"] is None:
            insertar_registro(data)
            mostrar_mensaje("Registro guardado")
        else:
            actualizar_registro(data + (editando_id["id"],))
            editando_id["id"] = None
            mostrar_mensaje("Registro actualizado")

        limpiar()
        cargar_tabla()

    # ---------- LIMPIAR ----------
    def limpiar():
        input_tipo.value = "GASTO"
        input_monto.value = ""
        input_cuenta.value = "EFECTIVO"
        input_categoria.value = "SIN CATEGORIA"
        input_descripcion.value = ""
        input_fecha.value = datetime.now().strftime("%Y-%m-%d")
        page.update()

    # ---------- TABLA ----------
    tabla = ft.Column()

    def cargar_tabla():
        tabla.controls.clear()

        for row in obtener_ultimos():
            rid = row[0]

            def editar_click(e, r=row):
                editando_id["id"] = r[0]
                input_tipo.value = r[1]
                input_monto.value = formato_miles(r[2])
                input_cuenta.value = r[3]
                input_categoria.value = r[4]
                input_descripcion.value = r[5]
                input_fecha.value = r[6]
                page.update()

            def borrar_click(e, rid=rid):
                eliminar_registro(rid)
                cargar_tabla()

            tabla.controls.append(
                ft.Container(
                    padding=8,
                    border=ft.border.all(1),
                    border_radius=10,
                    content=ft.Row([
                        ft.Text(str(row[0]), width=40),
                        ft.Text(row[1], width=80),
                        ft.Text("$ " + formato_miles(row[2]), width=110),
                        ft.Text(row[3], width=90),
                        ft.Text(row[4], width=120),
                        ft.Text(row[5], width=260),
                        ft.Text(row[6], width=100),
                        ft.IconButton(ft.Icons.EDIT, on_click=editar_click),
                        ft.IconButton(ft.Icons.DELETE, on_click=borrar_click),
                    ])
                )
            )

        page.update()


    # ---------- CONTROLES ----------

    input_tipo = ft.Dropdown(
        label="Tipo",
        width=200,
        value="GASTO",
        options=[
            ft.dropdown.Option("GASTO"),
            ft.dropdown.Option("INGRESO"),
            ft.dropdown.Option("AHORRO"),
        ]
    )

    # MONTO
    input_monto = ft.TextField(label="Monto", width=200)

    def monto_change(e):
        valor = re.sub(r"\D", "", e.control.value)
        if valor:
            e.control.value = formato_miles(valor)
        else:
            e.control.value = ""
        page.update()

    input_monto.on_change = monto_change

    input_cuenta = ft.Dropdown(
        label="Cuenta",
        width=200,
        value="EFECTIVO",
        options=[
            ft.dropdown.Option("EFECTIVO"),
            ft.dropdown.Option("CREDITO"),
            ft.dropdown.Option("AHORRO"),
        ]
    )

    input_categoria = ft.Dropdown(
        label="Categoría",
        width=200,
        value="SIN CATEGORIA",
        options=[
            ft.dropdown.Option("SIN CATEGORIA"),
            ft.dropdown.Option("A"),
            ft.dropdown.Option("B"),
            ft.dropdown.Option("C"),
        ]
    )

    input_descripcion = ft.TextField(label="Descripción", width=410, max_length=40)

    def descripcion_change(e):
        e.control.value = e.control.value.upper()
        page.update()

    input_descripcion.on_change = descripcion_change

    # FECHA
    input_fecha = ft.TextField(
        width=200,
        value=datetime.now().strftime("%Y-%m-%d"),
        label="Fecha"
    )
    
    def fecha_change(e):
        valor = re.sub(r"\D", "", e.control.value)
        if valor:
            e.control.value = formato_fecha(valor)
        else:
            e.control.value = ""
        page.update()

        input_fecha.on_change = fecha_change


    boton_guardar = ft.FilledButton("Guardar", on_click=guardar_registro)
    boton_confirmar = ft.FilledButton("Confirmar")

    # ---------- LAYOUT ----------
    page.add(
        ft.Text("Registro Financiero", size=24, weight="bold"),
        ft.Row([input_tipo, input_monto]),
        ft.Row([input_cuenta, input_categoria]),
        input_descripcion,
        ft.Row([input_fecha, boton_guardar, boton_confirmar]),
        ft.Divider(),
        ft.Text("Últimos 5 registros", size=20),
        tabla
    )

    limpiar()
    cargar_tabla()


ft.app(target=main)
