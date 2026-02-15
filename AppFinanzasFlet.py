import time
import flet as ft
import sqlite3
import re
from datetime import datetime
import asyncio

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

    page.title = "CONTROL FINANZAS "
    ###page.scroll = ft.ScrollMode.AUTO
    page.window_maximized = True  # Maximiza la ventana

    editando_id = {"id": None}
    borrar_id = {"id": None}

    # ---------- FUNCIONES ----------

    def mostrar_mensaje(msg):
        texto_mensaje.value=msg
        page.update()


    def formato_miles(valor):
        return f"{int(valor):,}".replace(",", ".")

    def formato_fecha(valor):
        return re.sub(r"(\d{2})(\d{2})(\d{4})", r"\1/\2/\3", valor)


    def validar_descripcion(txt):
        return bool(re.fullmatch(r"[A-Z0-9.,+\- ]+", txt))
    
    def validar_fecha(fecha_str):
        # 1️⃣ Validar formato exacto dd-mm-yyyy
        patron = r"^\d{2}-\d{2}-\d{4}$"
        
        if not re.match(patron, fecha_str):
            return False
        
        # 2️⃣ Validar que la fecha exista realmente
        try:
            datetime.strptime(fecha_str, "%d-%m-%Y")
            return True
        except ValueError:
            return False
            
    def validar_monto(monto):
        try:
            valor = float(monto)
            return valor > 0
        except ValueError:
            return False
    # ---------- VALIDACIONES ----------


    # ---------- GUARDAR ----------
    def Borrar_registro(e):
        if not texto_id.value:
            mostrar_mensaje(">> ERROR: Seleccionar Registro")
            return
        id=texto_id.value
        eliminar_registro(id)
        mostrar_mensaje(">> OK: Registro Eliminado")
        limpiar_campos()
        cargar_tabla()


    def guardar_registro(e):
        monto = int(input_monto.value.replace(".", ""))
        if not validar_monto(monto):
            mostrar_mensaje(">> ERROR: Monto debe ser numerico y Mayor a 0")
            return

        if not input_descripcion.value.strip():
            mostrar_mensaje(">> ERROR: Descripción Obligatoria")
            return

        if not validar_descripcion(input_descripcion.value):
            mostrar_mensaje(">> ERROR: Descripción Inválida")
            return

        if not validar_fecha(input_fecha.value):
            mostrar_mensaje(">> ERROR: Fecha Inválida dd-mm-yyyy")
            return

        data = (
            input_tipo.value,
            monto,
            input_cuenta.value,
            input_categoria.value,
            input_descripcion.value,
            input_fecha.value,
        )

        if editando_id["id"] is None:
            insertar_registro(data)
            mostrar_mensaje(">> OK: Registro Guardado")
        else:
            actualizar_registro(data + (editando_id["id"],))
            editando_id["id"] = None
            mostrar_mensaje(">> OK: Registro Actualizado")

        limpiar_campos()
        cargar_tabla()


    # ---------- LIMPIAR ----------
    def limpiar_campos():
        texto_id.value=""
        input_tipo.value = "GASTO"
        input_monto.value = "0"
        input_cuenta.value = "EFECTIVO"
        input_categoria.value = "SIN CATEGORIA"
        input_descripcion.value = ""
        input_fecha.value = datetime.now().strftime("%d-%m-%Y")
        page.update()

    def limpiar_campos2():
        limpiar_campos()
        texto_mensaje.value=""
        page.update()

    # ---------- TABLA ----------
    tabla = ft.Column()

    def cargar_tabla():
        tabla.controls.clear()

        for row in obtener_ultimos():
            rid = row[0]

            def editar_click(e, r=row):
                texto_id.value=r[0]               
                editando_id["id"] = r[0]
                input_tipo.value = r[1]
                input_monto.value = formato_miles(r[2])
                input_cuenta.value = r[3]
                input_categoria.value = r[4]
                input_descripcion.value = r[5]
                input_fecha.value = r[6]
                page.update()

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
                    ])
                )
            )

        page.update()


    # ---------- CONTROLES ----------
    # ID

    texto_id = ft.Text("", size=24, weight="bold")

    # FECHA
    input_fecha = ft.TextField(
        width=140,
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


    input_tipo = ft.Dropdown(
        label="Tipo",
        width=140,
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
        width=140,
        value="EFECTIVO",
        options=[
            ft.dropdown.Option("EFECTIVO"),
            ft.dropdown.Option("CREDITO"),
            ft.dropdown.Option("AHORRO"),
        ]
    )

    input_categoria = ft.Dropdown(
        label="Categoría",
        width=350,
        value="SIN CATEGORIA",
        options=[
            ft.dropdown.Option("SIN CATEGORIA"),
            ft.dropdown.Option("CATEGORIA-A"),
            ft.dropdown.Option("CATEGORIA-B"),
            ft.dropdown.Option("CATEGORIA-C"),
        ]
    )

    input_descripcion = ft.TextField(
        label="Descripción", 
        width=500, 
        max_length=40)

    def descripcion_change(e):
        e.control.value = e.control.value.upper()
        page.update()

    input_descripcion.on_change = descripcion_change


    boton_limpiar = ft.FilledButton("Limpiar", on_click=limpiar_campos2)
    boton_guardar = ft.FilledButton("Guardar", on_click=guardar_registro)
    boton_eliminar = ft.FilledButton("Eliminar", on_click=Borrar_registro)

    # MENSAJE

    texto_mensaje = ft.Text("",size=20)


    # ---------- LAYOUT ----------
    page.add(

        ft.Row([ft.Text("Registro Financiero ", size=24, weight="bold"),texto_id]),
        ft.Row([input_fecha, input_tipo, input_monto]),
        ft.Row([input_cuenta, input_categoria]),
        ft.Row([input_descripcion]),
        ft.Divider(),
        ft.Row([boton_limpiar, boton_guardar, boton_eliminar,texto_mensaje]),
        ft.Divider(),
        tabla
    )

    limpiar_campos()
    cargar_tabla()


ft.app(target=main)
