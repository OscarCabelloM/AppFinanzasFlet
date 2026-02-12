import flet as ft
import sqlite3
import re
from datetime import datetime


DB_NAME = "G:\Mi unidad\DBSqllite\DBAppFinanzasFlet.db"

# ---------- BASE DE DATOS ----------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tab_registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        INSERT INTO tab_registros (tab_reg_tipo,tab_reg_monto,tab_reg_cuenta,tab_reg_categoria,tab_reg_descripcion,tab_reg_fecha)
        VALUES (?,?,?,?,?,?)
    """, data)
    conn.commit()
    conn.close()


def obtener_ultimos():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT * FROM tab_registros ORDER BY id DESC LIMIT 10")
    rows = cur.fetchall()
    conn.close()
    return rows


def eliminar_registro(rid):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("DELETE FROM tab_registros WHERE id=?", (rid,))
    conn.commit()
    conn.close()


def actualizar_registro(data):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        UPDATE tab_registros
        SET tab_reg_tipo=?, tab_reg_monto=?, tab_reg_cuenta=?, tab_reg_categoria=?, tab_reg_descripcion=?, tab_reg_fecha=?
        WHERE id=?
    """, data)
    conn.commit()
    conn.close()

# ---------- APP ----------

def main(page: ft.Page):
    init_db()

    page.title = "Control Finanzas"
    page.scroll = ft.ScrollMode.AUTO

    editando_id = {"id": None}

        # -------- VALIDACIONES --------
    def validar_input_descripcion(txt):
        return bool(re.fullmatch(r"[A-Za-z0-9.,+\- ]+", txt))

    
    def guardar_registro(e):
        if not input_monto.value.isdigit() or int(input_monto.value) <= 0:
            page.snack_bar = ft.SnackBar(ft.Text("Monto debe ser entero mayor a 0"))
            page.snack_bar.open = True
            page.update()
            return

        if not input_descripcion.value.strip():
            page.snack_bar = ft.SnackBar(ft.Text("Descripción obligatoria"))
            page.snack_bar.open = True
            page.update()
            return

        if not validar_input_descripcion(input_descripcion.value):
            page.snack_bar = ft.SnackBar(ft.Text("Descripción inválida"))
            page.snack_bar.open = True
            page.update()
            return

        if not input_fecha.value:
            page.snack_bar = ft.SnackBar(ft.Text("Seleccione fecha"))
            page.snack_bar.open = True
            page.update()
            return

        nuevo_registro = (
            input_tipo.value,
            int(input_monto.value),
            input_cuenta.value,
            input_categoria.value,
            input_descripcion.value,
            input_fecha.value,
        )

        if editando_id["id"] is None:
            insertar_registro(nuevo_registro)
        else:
            actualizar_registro(nuevo_registro + (editando_id["id"],))
            editando_id["id"] = None

        limpiar_campos_input()
        cargar_tabla_ultimos_10()

##        texto_mensaje.value="Registro Grabado correctamente."
#        page.update()


    def limpiar_campos_input():
        input_tipo.value = "GASTO"
        input_monto.value = ""
        input_cuenta.value = "EFECTIVO"
        input_categoria.value = "SIN CATEGORIA"
        input_descripcion.value = ""
        input_fecha.value = datetime.now().strftime("%Y-%m-%d")
        page.update()

    # -------- TABLA ULTIMOS 10 REGISTRO--------
    tabla_ultimos_10 = ft.Column()


    def cargar_tabla_ultimos_10():
        tabla_ultimos_10.controls.clear()
        datos = obtener_ultimos()

        for row in datos:
            rid = row[0]

            def editar_click(e, r=row):
                editando_id["id"] = r[0]
                input_tipo.value = r[1]
                input_monto.value = str(r[2])
                input_cuenta.value = r[3]
                input_categoria.value = r[4]
                input_descripcion.value = r[5]
                input_fecha.value = r[6]
                page.update()

            def borrar_click(e, rid=rid):
                eliminar_registro(rid)
                cargar_tabla_ultimos_10()
#                texto_mensaje.value="Registro Eliminado correctamente."
#                page.update()


            tabla_ultimos_10.controls.append(
                ft.Container(
                    padding=10,
                    border=ft.border.all(1),
                    border_radius=10,
                    content=ft.Row([
                        ft.Text(str(row[0]), width=40),
                        ft.Text(row[1], width=100),
                        ft.Text(str(row[2]), width=100),
                        ft.Text(row[3], width=90),
                        ft.Text(row[4], width=120),
                        ft.Text(row[5], width=400),
                        ft.Text(row[6], width=100),
                        ft.IconButton(ft.Icons.EDIT, on_click=editar_click),
                        ft.IconButton(ft.Icons.DELETE, on_click=borrar_click),
                    ])
                )
            )

        page.update()

    # -------- CONTROLES --------

    input_tipo = ft.Dropdown(
        label="Tipo Ingreso",
        value="GASTO",
        width=200,
        options=[
            ft.dropdown.Option("GASTO"),
            ft.dropdown.Option("INGRESO"),
            ft.dropdown.Option("AHORRO"),
        ]
    )

    input_monto = ft.TextField(
        width=200,
        label="Monto", 
        keyboard_type=ft.KeyboardType.NUMBER,
        )
    

    def monto_blur(e):
        input_monto.border_color = None
        page.update()


    input_monto.on_blur = monto_blur

    input_cuenta = ft.Dropdown(
        label="Tipo Pago",
        value="EFECTIVO",
        width=200,
        options=[
            ft.dropdown.Option("EFECTIVO"),
            ft.dropdown.Option("CREDITO"),
            ft.dropdown.Option("AHORRO"),
        ]
    )

    input_categoria = ft.Dropdown(
        width=200,
        label="Categoría",
        value="SIN CATEGORIA",
        options=[
            ft.dropdown.Option("SIN CATEGORIA"),
            ft.dropdown.Option("input_categoria A"),
            ft.dropdown.Option("input_categoria B"),
            ft.dropdown.Option("input_categoria C"),
        ]
    )

    input_descripcion = ft.TextField(
        width=410,
        max_length=40,
        label="Descripción")


    def input_descripcion_change(e):
        texto = e.control.value.upper()
        if e.control.value != texto:
            e.control.value = texto
            page.update()


    input_descripcion.on_change = input_descripcion_change

    input_fecha = ft.TextField(
        width=200,
        value=datetime.now().strftime("%Y-%m-%d"),
        label="Fecha")

    date_picker = ft.DatePicker()

    def input_seleccionar_fecha(e):
        date_picker.open = True
        page.update()


    def input_fecha_cambiada(e):
        if e.value:
            input_fecha.value = e.value.strftime("%Y-%m-%d")
            page.update()


    date_picker.on_change = input_fecha_cambiada
    page.overlay.append(date_picker)


    input_fecha_cambiada.on_focus = input_seleccionar_fecha

    boton_guardar = ft.FilledButton("Guardar", on_click=guardar_registro)

    # texto_mensaje = ft.Text("", size= 16 ,alignment=ft.MainAxisAlignment.CENTER)

    # -------- LAYOUT --------

    page.add(
        ft.Text("Registro Financiero", size=24, weight="bold"),
        ft.Row([input_tipo, input_monto]),
        ft.Row([input_cuenta, input_categoria]),
        ft.Row([input_descripcion]),
        ft.Row([input_fecha,boton_guardar]),
#        ft.Row([texto_mensaje]),
        ft.Divider(),
        ft.Text("Últimos 10 registros", size=20),
        tabla_ultimos_10
    )

    limpiar_campos_input()
    cargar_tabla_ultimos_10()


ft.app(target=main)
