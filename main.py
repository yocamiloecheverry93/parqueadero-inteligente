import tkinter as tk
from tkinter import ttk, messagebox
from sistema import SistemaParqueadero
from modelos import (
    ESTADO_LIBRE,
    ESTADO_OCUPADO,
    ESTADO_MANTENIMIENTO,
    ZONA_EXPRESS,
    CAT_CARRO_ESTANDAR,
    CAT_CAMIONETA_SUV,
    CAT_MOTO,
    MOD_EXPRESS,
    MOD_NORMAL,
    MOD_LARGA,
    LETRAS_FILA,
)

COLORES = {
    "LIBRE_NORMAL": "#2ecc71",      # Verde
    "LIBRE_EXPRESS": "#3498db",     # Azul
    "OCUPADO": "#e74c3c",           # Rojo
    "MANTENIMIENTO": "#f39c12",     # Amarillo/Ámbar
    "LOCALIZADO": "#9b59b6",        # Morado destacado
}


class AplicacionParqueadero(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Parqueadero Inteligente 24/7 — Estructuras de Datos (Python)")
        self.geometry("1280x760")
        self.configure(bg="#f4f6f9")

        self.sistema = SistemaParqueadero()
        self.botones_mapa = {}          # (piso, fila, col) -> tk.Button
        self.puesto_resaltado = None    # Código del puesto resaltado por el localizador

        self._construir_encabezado()
        self._construir_cuerpo()
        self.refrescar_todo()

    # --------------------------------------------------------------------------
    # CONSTRUCCIÓN DE LA INTERFAZ
    # --------------------------------------------------------------------------
    def _construir_encabezado(self):
        header = tk.Frame(self, bg="#1e272e", pady=10, padx=15)
        header.pack(fill="x")

        tk.Label(
            header,
            text="SISTEMA DE PARQUEADERO INTELIGENTE (80 ESPACIOS - 2 PISOS)",
            font=("Segoe UI", 14, "bold"),
            fg="white",
            bg="#1e272e",
        ).pack(side="left")

        self.lbl_stats = tk.Label(
            header,
            text="",
            font=("Segoe UI", 10, "bold"),
            fg="#ffd32a",
            bg="#1e272e",
        )
        self.lbl_stats.pack(side="right")

    def _construir_cuerpo(self):
        contenedor = tk.Frame(self, bg="#f4f6f9", padx=12, pady=10)
        contenedor.pack(fill="both", expand=True)

        # Panel izquierdo: Mapa interactivo de los 2 pisos
        panel_izq = tk.Frame(contenedor, bg="#f4f6f9")
        panel_izq.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self._construir_leyenda(panel_izq)

        self.notebook_pisos = ttk.Notebook(panel_izq)
        self.notebook_pisos.pack(fill="both", expand=True, pady=(6, 0))

        for piso, titulo in [
            (1, "Piso 1 — Zona Express (A, B) y Normal / SUV (C, D)"),
            (2, "Piso 2 — Larga Estadía: Carros Estándar (A, B) y Motos (C, D)"),
        ]:
            tab = tk.Frame(self.notebook_pisos, bg="white", padx=10, pady=10)
            self.notebook_pisos.add(tab, text=titulo)
            self._construir_grilla_piso(tab, piso)

        tk.Label(
            panel_izq,
            text="Tip: Haz clic en un puesto LIBRE/MANTENIMIENTO para bloquearlo o habilitarlo; haz clic en uno OCUPADO para ver sus datos.",
            font=("Segoe UI", 9, "italic"),
            bg="#f4f6f9",
            fg="#57606f",
        ).pack(anchor="w", pady=(6, 0))

        # Panel derecho: Controles e Innovaciones
        panel_der = tk.Frame(contenedor, bg="#f4f6f9", width=430)
        panel_der.pack(side="right", fill="y")
        panel_der.pack_propagate(False)

        self.notebook_ctrl = ttk.Notebook(panel_der)
        self.notebook_ctrl.pack(fill="both", expand=True)

        self._construir_tab_ingreso()
        self._construir_tab_localizador_salida()
        self._construir_tab_estructuras()

    def _construir_leyenda(self, padre):
        barra = tk.Frame(padre, bg="#f4f6f9")
        barra.pack(fill="x")

        items = [
            ("Libre Normal", COLORES["LIBRE_NORMAL"]),
            ("Libre Express", COLORES["LIBRE_EXPRESS"]),
            ("Ocupado", COLORES["OCUPADO"]),
            ("Mantenimiento", COLORES["MANTENIMIENTO"]),
            ("Localizado", COLORES["LOCALIZADO"]),
        ]
        for texto, color in items:
            tk.Label(barra, bg=color, width=2).pack(side="left", padx=(0, 4))
            tk.Label(barra, text=texto, bg="#f4f6f9", font=("Segoe UI", 9)).pack(
                side="left", padx=(0, 12)
            )

    def _construir_grilla_piso(self, padre, piso):
        # Encabezado de columnas (1..10)
        tk.Label(padre, text="Fila", bg="white", font=("Segoe UI", 9, "bold")).grid(
            row=0, column=0, padx=4, pady=4
        )
        for col in range(10):
            tk.Label(padre, text=f"#{col + 1}", bg="white", font=("Segoe UI", 9, "bold")).grid(
                row=0, column=col + 1, padx=3, pady=4
            )

        for fila in range(4):
            puesto_ejemplo = self.sistema.matrices[piso].obtener_celda(fila, 0)
            etiqueta = f"{LETRAS_FILA[fila]}\n({puesto_ejemplo.tipo_base[0]}-{puesto_ejemplo.zona[0]})"
            tk.Label(
                padre,
                text=etiqueta,
                bg="white",
                font=("Segoe UI", 8, "bold"),
                fg="#2f3542",
            ).grid(row=fila + 1, column=0, padx=4, pady=4)

            for col in range(10):
                btn = tk.Button(
                    padre,
                    text="",
                    width=7,
                    height=3,
                    font=("Segoe UI", 8, "bold"),
                    fg="white",
                    relief="raised",
                    cursor="hand2",
                    command=lambda p=piso, f=fila, c=col: self._clic_puesto(p, f, c),
                )
                btn.grid(row=fila + 1, column=col + 1, padx=3, pady=4, sticky="nsew")
                self.botones_mapa[(piso, fila, col)] = btn

        for col in range(1, 11):
            padre.grid_columnconfigure(col, weight=1)

    def _construir_tab_ingreso(self):
        tab = tk.Frame(self.notebook_ctrl, bg="white", padx=14, pady=12)
        self.notebook_ctrl.add(tab, text="1. Ingreso (ABB)")

        tk.Label(
            tab, text="Asignación Inteligente de Puesto", font=("Segoe UI", 11, "bold"), bg="white"
        ).pack(anchor="w", pady=(0, 10))

        tk.Label(tab, text="Placa del vehículo:", bg="white", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.ent_placa = tk.Entry(tab, font=("Segoe UI", 11))
        self.ent_placa.pack(fill="x", pady=(2, 10))

        tk.Label(tab, text="Tipo / Tamaño del vehículo:", bg="white", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.var_categoria = tk.StringVar(value=CAT_CARRO_ESTANDAR)
        opciones_cat = [
            ("Automóvil Estándar (Piso 1 o 2)", CAT_CARRO_ESTANDAR),
            ("Camioneta / SUV (Solo Piso 1 por altura)", CAT_CAMIONETA_SUV),
            ("Motocicleta", CAT_MOTO),
        ]
        for texto, val in opciones_cat:
            tk.Radiobutton(
                tab, text=texto, variable=self.var_categoria, value=val, bg="white"
            ).pack(anchor="w")

        tk.Label(
            tab, text="Tiempo estimado de estadía:", bg="white", font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", pady=(10, 0))
        self.var_modalidad = tk.StringVar(value=MOD_EXPRESS)
        opciones_mod = [
            ("Parada Express (<= 15 min) — Piso 1 más cercano", MOD_EXPRESS),
            ("Estadía Normal (1 a 3 h) — Más cercano disponible", MOD_NORMAL),
            ("Larga Estadía (+3 h) — Zona más lejana (ABB inverso)", MOD_LARGA),
        ]
        for texto, val in opciones_mod:
            tk.Radiobutton(
                tab, text=texto, variable=self.var_modalidad, value=val, bg="white"
            ).pack(anchor="w")

        tk.Button(
            tab,
            text="Asignar Puesto Inteligentemente",
            bg="#1e90ff",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            pady=7,
            cursor="hand2",
            command=self._accion_ingresar,
        ).pack(fill="x", pady=(14, 6))

        tk.Button(
            tab,
            text="Cargar Datos de Prueba (Demo Rápida)",
            bg="#57606f",
            fg="white",
            font=("Segoe UI", 9),
            pady=4,
            cursor="hand2",
            command=self._cargar_demo,
        ).pack(fill="x", pady=(0, 10))

        tk.Label(tab, text="Resultado de asignación y ruta:", bg="white", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.txt_ingreso = tk.Text(tab, height=11, font=("Consolas", 9), bg="#f8f9fa", wrap="word")
        self.txt_ingreso.pack(fill="both", expand=True, pady=(4, 0))

    def _construir_tab_localizador_salida(self):
        tab = tk.Frame(self.notebook_ctrl, bg="white", padx=14, pady=12)
        self.notebook_ctrl.add(tab, text="2. Localizador / Salida")

        tk.Label(
            tab, text="Localizador (Tabla Hash + Lista de Ruta)", font=("Segoe UI", 11, "bold"), bg="white"
        ).pack(anchor="w", pady=(0, 8))

        tk.Label(tab, text="Placa o Código de Tiquete (ej: ABC123 o TK-0001):", bg="white", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.ent_buscar = tk.Entry(tab, font=("Segoe UI", 11))
        self.ent_buscar.pack(fill="x", pady=(2, 8))

        frame_btns = tk.Frame(tab, bg="white")
        frame_btns.pack(fill="x", pady=(0, 10))

        tk.Button(
            frame_btns,
            text="Localizar en Mapa",
            bg="#8e44ad",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            pady=6,
            cursor="hand2",
            command=self._accion_localizar,
        ).pack(side="left", fill="x", expand=True, padx=(0, 4))

        tk.Button(
            frame_btns,
            text="Limpiar Resaltado",
            bg="#95a5a6",
            fg="white",
            font=("Segoe UI", 9),
            pady=6,
            cursor="hand2",
            command=self._limpiar_resaltado,
        ).pack(side="right")

        ttk.Separator(tab, orient="horizontal").pack(fill="x", pady=8)

        tk.Label(
            tab, text="Registro de Salida y Cobro", font=("Segoe UI", 10, "bold"), bg="white"
        ).pack(anchor="w")

        tk.Label(
            tab,
            text="Minutos a simular (dejar vacío para tiempo real):",
            bg="white",
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(4, 0))
        self.ent_minutos = tk.Entry(tab, font=("Segoe UI", 10))
        self.ent_minutos.pack(fill="x", pady=(2, 8))

        tk.Button(
            tab,
            text="Registrar Salida y Calcular Tarifa",
            bg="#e74c3c",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            pady=7,
            cursor="hand2",
            command=self._accion_salida,
        ).pack(fill="x", pady=(0, 10))

        tk.Label(tab, text="Ruta peatonal / Detalle de factura:", bg="white", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.txt_loc_salida = tk.Text(tab, height=13, font=("Consolas", 9), bg="#f8f9fa", wrap="word")
        self.txt_loc_salida.pack(fill="both", expand=True, pady=(4, 0))

    def _construir_tab_estructuras(self):
        tab = tk.Frame(self.notebook_ctrl, bg="white", padx=12, pady=10)
        self.notebook_ctrl.add(tab, text="3. Cola / Pila / ABB")

        # Botón Deshacer (Pila LIFO)
        tk.Button(
            tab,
            text="Deshacer Última Acción (Pila LIFO)",
            bg="#d35400",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            pady=6,
            cursor="hand2",
            command=self._accion_deshacer,
        ).pack(fill="x", pady=(0, 6))

        tk.Button(
            tab,
            text="Inspeccionar Recorrido InOrden del ABB",
            bg="#16a085",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            pady=5,
            cursor="hand2",
            command=self._mostrar_abb,
        ).pack(fill="x", pady=(0, 8))

        tk.Label(tab, text="Cola de Espera (FIFO):", bg="white", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.lst_cola = tk.Listbox(tab, height=5, font=("Consolas", 8))
        self.lst_cola.pack(fill="x", pady=(2, 6))

        tk.Label(tab, text="Pila de Auditoría / Undo (LIFO - tope arriba):", bg="white", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.lst_pila = tk.Listbox(tab, height=6, font=("Consolas", 8))
        self.lst_pila.pack(fill="x", pady=(2, 6))

        tk.Label(tab, text="Historial de Facturas (Lista Enlazada):", bg="white", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.lst_facturas = tk.Listbox(tab, height=7, font=("Consolas", 8))
        self.lst_facturas.pack(fill="both", expand=True, pady=(2, 0))

    # --------------------------------------------------------------------------
    # ACCIONES E INTERACCIÓN
    # --------------------------------------------------------------------------
    def _clic_puesto(self, piso, fila, col):
        puesto = self.sistema.matrices[piso].obtener_celda(fila, col)
        if puesto.estado == ESTADO_OCUPADO:
            v = puesto.vehiculo_actual
            self.ent_buscar.delete(0, tk.END)
            self.ent_buscar.insert(0, v.placa)
            self.notebook_ctrl.select(1)
            self._accion_localizar()
        else:
            accion = "bloquear en MANTENIMIENTO" if puesto.estado == ESTADO_LIBRE else "habilitar como LIBRE"
            if messagebox.askyesno("Mantenimiento", f"¿Deseas {accion} el puesto {puesto.codigo}?"):
                res = self.sistema.alternar_mantenimiento(piso, fila, col)
                messagebox.showinfo("Mantenimiento", res["mensaje"])
                self.refrescar_todo()

    def _accion_ingresar(self):
        placa = self.ent_placa.get()
        cat = self.var_categoria.get()
        mod = self.var_modalidad.get()

        res = self.sistema.ingresar_vehiculo(placa, cat, mod)
        self.txt_ingreso.delete("1.0", tk.END)

        if not res["ok"]:
            messagebox.showwarning("Ingreso", res["mensaje"])
            return

        self.ent_placa.delete(0, tk.END)
        self.txt_ingreso.insert(tk.END, res["mensaje"] + "\n")

        if not res["en_cola"]:
            puesto = res["puesto"]
            self.puesto_resaltado = puesto.codigo
            self.notebook_pisos.select(puesto.piso - 1)
            self.txt_ingreso.insert(tk.END, "\nRuta sugerida (Lista Enlazada):\n")
            for paso in res["ruta"]:
                self.txt_ingreso.insert(tk.END, f"  {paso}\n")

        self.refrescar_todo()

    def _accion_localizar(self):
        criterio = self.ent_buscar.get()
        res = self.sistema.localizar_vehiculo(criterio)
        self.txt_loc_salida.delete("1.0", tk.END)

        if not res["ok"]:
            messagebox.showwarning("Localizador", res["mensaje"])
            return

        v = res["vehiculo"]
        p = res["puesto"]
        self.puesto_resaltado = p.codigo
        self.notebook_pisos.select(p.piso - 1)

        info = (
            f"VEHÍCULO LOCALIZADO (Tabla Hash O(1))\n"
            f"--------------------------------------\n"
            f"Placa:     {v.placa}\n"
            f"Tiquete:   {v.codigo_tiquete}\n"
            f"Tipo:      {v.etiqueta_categoria()}\n"
            f"Ubicación: Piso {p.piso} | Fila {p.letra_fila} | Puesto #{p.columna + 1} ({p.codigo})\n"
            f"Zona:      {p.zona}\n"
            f"Ingreso:   {v.hora_ingreso.strftime('%H:%M:%S')}\n\n"
            f"RUTA PEATONAL (Lista Enlazada):\n"
        )
        for paso in res["ruta"]:
            info += f"  {paso}\n"

        self.txt_loc_salida.insert(tk.END, info)
        self.refrescar_todo()

    def _limpiar_resaltado(self):
        self.puesto_resaltado = None
        self.refrescar_todo()

    def _accion_salida(self):
        criterio = self.ent_buscar.get()
        min_txt = self.ent_minutos.get().strip()
        minutos_sim = None

        if min_txt:
            try:
                minutos_sim = float(min_txt)
                if minutos_sim <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Los minutos simulados deben ser un número positivo.")
                return

        res = self.sistema.registrar_salida(criterio, minutos_sim)
        if not res["ok"]:
            messagebox.showwarning("Salida", res["mensaje"])
            return

        f = res["factura"]
        self.puesto_resaltado = None
        self.ent_buscar.delete(0, tk.END)
        self.ent_minutos.delete(0, tk.END)

        recibo = (
            f"========= FACTURA DE SALIDA =========\n"
            f"Tiquete:  {f['tiquete']}\n"
            f"Placa:    {f['placa']} ({f['categoria']})\n"
            f"Puesto:   {f['puesto']} ({f['zona']})\n"
            f"Tiempo:   {f['minutos']} minutos\n"
            f"Detalle:  {f['detalle']}\n"
            f"TOTAL A PAGAR: ${f['total']:,}\n"
            f"=====================================\n"
        )
        if res["auto_asignado"]:
            recibo += f"\n>>> {res['auto_asignado']}\n"

        self.txt_loc_salida.delete("1.0", tk.END)
        self.txt_loc_salida.insert(tk.END, recibo)
        self.refrescar_todo()

    def _accion_deshacer(self):
        res = self.sistema.deshacer_ultima_accion()
        if res["ok"]:
            messagebox.showinfo("Deshacer (Pila LIFO)", res["mensaje"])
        else:
            messagebox.showwarning("Deshacer (Pila LIFO)", res["mensaje"])
        self.refrescar_todo()

    def _mostrar_abb(self):
        elementos = self.sistema.arbol_disponibles.recorrido_inorden()
        ventana = tk.Toplevel(self)
        ventana.title("Recorrido InOrden del ABB (Puestos Libres por Cercanía)")
        ventana.geometry("540x420")

        txt = tk.Text(ventana, font=("Consolas", 9), padx=8, pady=8)
        txt.pack(fill="both", expand=True)
        txt.insert(
            tk.END,
            f"Total puestos libres indexados en el ABB: {len(elementos)}\n"
            f"(Ordenados de menor a mayor distancia a la salida)\n"
            f"{'-' * 58}\n",
        )
        for clave, puesto in elementos:
            suv_txt = "SUV OK" if puesto.permite_suv else "Std"
            txt.insert(
                tk.END,
                f"Puntaje {clave} -> {puesto.codigo} | {puesto.tipo_base:<5} | {puesto.zona:<7} | {suv_txt}\n",
            )

    def _cargar_demo(self):
        pruebas = [
            ("EXP101", CAT_CARRO_ESTANDAR, MOD_EXPRESS),
            ("EXP102", CAT_CAMIONETA_SUV, MOD_EXPRESS),
            ("MEX201", CAT_MOTO, MOD_EXPRESS),
            ("SUV301", CAT_CAMIONETA_SUV, MOD_LARGA),
            ("LRG401", CAT_CARRO_ESTANDAR, MOD_LARGA),
            ("LRG402", CAT_CARRO_ESTANDAR, MOD_LARGA),
            ("NRM501", CAT_CARRO_ESTANDAR, MOD_NORMAL),
            ("MOT601", CAT_MOTO, MOD_LARGA),
        ]
        cargados = 0
        for placa, cat, mod in pruebas:
            res = self.sistema.ingresar_vehiculo(placa, cat, mod)
            if res["ok"]:
                cargados += 1
        self.refrescar_todo()
        messagebox.showinfo("Demo cargada", f"Se ingresaron {cargados} vehículos de prueba en distintas zonas.")

    # --------------------------------------------------------------------------
    # REFRESCO VISUAL COMPLETO
    # --------------------------------------------------------------------------
    def refrescar_todo(self):
        # 1. Estadísticas superiores
        st = self.sistema.obtener_estadisticas()
        self.lbl_stats.config(
            text=(
                f"Libres (ABB): {st['libres']}  |  Ocupados: {st['ocupados']}  |  "
                f"Mant.: {st['mantenimiento']}  |  Cola: {st['en_cola']}  |  "
                f"Recaudado: ${st['recaudado']:,}"
            )
        )

        # 2. Actualizar botones de las 2 matrices
        for (piso, fila, col), btn in self.botones_mapa.items():
            puesto = self.sistema.matrices[piso].obtener_celda(fila, col)
            icono = "C" if puesto.tipo_base == "CARRO" else "M"
            etiqueta_top = f"{puesto.letra_fila}{col + 1:02d} [{icono}]"

            if puesto.codigo == self.puesto_resaltado:
                color = COLORES["LOCALIZADO"]
                sub = puesto.vehiculo_actual.placa if puesto.vehiculo_actual else "AQUÍ"
            elif puesto.estado == ESTADO_OCUPADO:
                color = COLORES["OCUPADO"]
                sub = puesto.vehiculo_actual.placa
            elif puesto.estado == ESTADO_MANTENIMIENTO:
                color = COLORES["MANTENIMIENTO"]
                sub = "MANT."
            else:
                color = COLORES["LIBRE_EXPRESS"] if puesto.zona == ZONA_EXPRESS else COLORES["LIBRE_NORMAL"]
                sub = "EXPR" if puesto.zona == ZONA_EXPRESS else "LIBRE"

            btn.config(text=f"{etiqueta_top}\n{sub}", bg=color, activebackground=color)

        # 3. Actualizar Cola de Espera
        self.lst_cola.delete(0, tk.END)
        for idx, v in enumerate(self.sistema.cola_espera.listar_elementos(), start=1):
            self.lst_cola.insert(tk.END, f"#{idx} | {v.placa} | {v.etiqueta_categoria()} | {v.modalidad}")

        # 4. Actualizar Pila de Auditoría
        self.lst_pila.delete(0, tk.END)
        for acc in self.sistema.pila_acciones.listar_elementos():
            self.lst_pila.insert(tk.END, acc["descripcion"])

        # 5. Actualizar Historial de Facturas (Lista Enlazada)
        self.lst_facturas.delete(0, tk.END)
        for fac in self.sistema.historial_facturas.recorrer():
            self.lst_facturas.insert(
                tk.END,
                f"{fac['hora_salida']} | {fac['placa']} ({fac['puesto']}) | {fac['minutos']}m | ${fac['total']:,}",
            )


if __name__ == "__main__":
    app = AplicacionParqueadero()
    app.mainloop()