from datetime import datetime
from estructuras import (
    ListaEnlazada,
    Pila,
    Cola,
    TablaHash,
    ArbolBinarioBusqueda,
    MatrizParqueadero,
)
from modelos import (
    Puesto,
    Vehiculo,
    calcular_tarifa,
    ESTADO_LIBRE,
    ESTADO_OCUPADO,
    ESTADO_MANTENIMIENTO,
    ZONA_EXPRESS,
    ZONA_NORMAL,
    CAT_CAMIONETA_SUV,
    CAT_MOTO,
    MOD_EXPRESS,
    MOD_NORMAL,
    MOD_LARGA,
)


class SistemaParqueadero:
    def __init__(self):
        # 1. Matrices: 2 pisos de 4x10 (80 puestos totales)
        self.matrices = {
            1: MatrizParqueadero(piso=1, filas=4, columnas=10),
            2: MatrizParqueadero(piso=2, filas=4, columnas=10),
        }
        # 2. Árbol Binario de Búsqueda con todos los puestos LIBRES ordenados por cercanía
        self.arbol_disponibles = ArbolBinarioBusqueda()
        # 3. Tablas Hash (Diccionarios) para búsqueda O(1) por placa y por código de tiquete
        self.tabla_placas = TablaHash()
        self.tabla_tiquetes = TablaHash()
        # 4. Cola FIFO de espera cuando no hay puestos disponibles
        self.cola_espera = Cola()
        # 5. Pila LIFO de auditoría y botón Deshacer (Undo)
        self.pila_acciones = Pila()
        # 6. Lista Enlazada de historial de facturas cerradas
        self.historial_facturas = ListaEnlazada()

        self._contador_tiquetes = 1
        self.total_recaudado = 0
        self._inicializar_puestos()

    def _inicializar_puestos(self):
        """
        Configura exactamente los 80 espacios especificados:
        Piso 1: Fila A = 10 Carros Express | Fila B = 10 Motos Express | Filas C,D = 20 Carros Normal (SUV OK)
        Piso 2: Filas A,B = 20 Carros Normal (solo estándar) | Filas C,D = 20 Motos Normal
        """
        config_pisos = {
            1: [
                (ZONA_EXPRESS, "CARRO", True),   # Fila A (10)
                (ZONA_EXPRESS, "MOTO", False),   # Fila B (10)
                (ZONA_NORMAL, "CARRO", True),    # Fila C (10)
                (ZONA_NORMAL, "CARRO", True),    # Fila D (10)
            ],
            2: [
                (ZONA_NORMAL, "CARRO", False),   # Fila A (10 - restricción altura SUV)
                (ZONA_NORMAL, "CARRO", False),   # Fila B (10 - restricción altura SUV)
                (ZONA_NORMAL, "MOTO", False),    # Fila C (10)
                (ZONA_NORMAL, "MOTO", False),    # Fila D (10)
            ],
        }

        for piso, filas_cfg in config_pisos.items():
            matriz = self.matrices[piso]
            for fila_idx, (zona, tipo_base, permite_suv) in enumerate(filas_cfg):
                for col_idx in range(10):
                    puesto = Puesto(piso, fila_idx, col_idx, zona, tipo_base, permite_suv)
                    matriz.asignar_celda(fila_idx, col_idx, puesto)
                    self.arbol_disponibles.insertar(puesto.distancia_salida, puesto)

    def _generar_codigo_tiquete(self):
        codigo = f"TK-{self._contador_tiquetes:04d}"
        self._contador_tiquetes += 1
        return codigo

    def _buscar_puesto_inteligente(self, vehiculo):
        """
        INNOVACIÓN 2: Asignación inteligente usando el ABB ordenado por cercanía.
        - Express: más cercano en zona Express (InOrden).
        - Normal (1-3h): más cercano en zona Normal (InOrden).
        - Larga Estadía (+3h): más lejano en zona Normal (InOrden inverso) para dejar
          despejados los accesos cercanos a la salida.
        - SUV: siempre restringida a puestos con permite_suv=True (Piso 1).
        """
        zona_objetivo = ZONA_EXPRESS if vehiculo.modalidad == MOD_EXPRESS else ZONA_NORMAL
        es_suv = vehiculo.categoria == CAT_CAMIONETA_SUV
        buscar_mas_lejano = vehiculo.modalidad == MOD_LARGA

        def es_compatible(puesto):
            if puesto.estado != ESTADO_LIBRE:
                return False
            if puesto.tipo_base != vehiculo.tipo_base:
                return False
            if puesto.zona != zona_objetivo:
                return False
            if es_suv and not puesto.permite_suv:
                return False
            return True

        return self.arbol_disponibles.buscar_primero_que_cumpla(
            es_compatible, inverso=buscar_mas_lejano
        )

    def _vehiculo_en_cola(self, placa):
        placa_norm = placa.strip().upper()
        for v in self.cola_espera.listar_elementos():
            if v.placa == placa_norm:
                return True
        return False

    def ingresar_vehiculo(self, placa, categoria, modalidad):
        placa_norm = placa.strip().upper()
        if not placa_norm or len(placa_norm) < 4:
            return {"ok": False, "mensaje": "Ingresa una placa válida (mínimo 4 caracteres)."}

        if self.tabla_placas.contiene(placa_norm):
            return {"ok": False, "mensaje": f"El vehículo {placa_norm} ya se encuentra parqueado."}

        if self._vehiculo_en_cola(placa_norm):
            return {"ok": False, "mensaje": f"El vehículo {placa_norm} ya está en la cola de espera."}

        tiquete = self._generar_codigo_tiquete()
        vehiculo = Vehiculo(placa_norm, categoria, modalidad, tiquete)
        puesto = self._buscar_puesto_inteligente(vehiculo)

        if puesto is None:
            # INNOVACIÓN 3: Encolar automáticamente si no hay espacio compatible
            self.cola_espera.encolar(vehiculo)
            return {
                "ok": True,
                "en_cola": True,
                "vehiculo": vehiculo,
                "posicion_cola": len(self.cola_espera),
                "mensaje": (
                    f"No hay puestos libres para {vehiculo.etiqueta_categoria()} ({modalidad}). "
                    f"Vehículo {placa_norm} agregado a la Cola de Espera (Turno #{len(self.cola_espera)})."
                ),
            }

        self._asignar_vehiculo_a_puesto(vehiculo, puesto, registrar_en_pila=True)
        ruta = self.construir_ruta_peatonal(puesto)
        return {
            "ok": True,
            "en_cola": False,
            "vehiculo": vehiculo,
            "puesto": puesto,
            "ruta": ruta.recorrer(),
            "mensaje": (
                f"Ingreso exitoso. Tiquete {vehiculo.codigo_tiquete}. "
                f"Diríjase al Piso {puesto.piso}, Fila {puesto.letra_fila}, Puesto {puesto.columna + 1} "
                f"({puesto.codigo} - Zona {puesto.zona})."
            ),
        }

    def _asignar_vehiculo_a_puesto(self, vehiculo, puesto, registrar_en_pila=True):
        self.arbol_disponibles.eliminar(puesto.distancia_salida)
        puesto.estado = ESTADO_OCUPADO
        puesto.vehiculo_actual = vehiculo
        vehiculo.puesto_asignado = puesto

        self.tabla_placas.insertar(vehiculo.placa, vehiculo)
        self.tabla_tiquetes.insertar(vehiculo.codigo_tiquete, vehiculo)

        if registrar_en_pila:
            self.pila_acciones.apilar({
                "tipo": "INGRESO",
                "placa": vehiculo.placa,
                "tiquete": vehiculo.codigo_tiquete,
                "piso": puesto.piso,
                "fila": puesto.fila,
                "col": puesto.columna,
                "descripcion": f"Ingreso {vehiculo.placa} ({vehiculo.codigo_tiquete}) -> {puesto.codigo}",
            })

    def construir_ruta_peatonal(self, puesto):
        """
        INNOVACIÓN 1: Construye la ruta sugerida paso a paso usando una Lista Enlazada.
        """
        ruta = ListaEnlazada()
        ruta.agregar_al_final("1. Ingresa por el Acceso Peatonal Principal (Piso 1).")

        if puesto.piso == 1:
            ruta.agregar_al_final("2. Permanece en el Piso 1 (nivel calle).")
        else:
            ruta.agregar_al_final("2. Sube por las Escaleras o Ascensor A hacia el Piso 2.")

        tipo_zona = "Zona Express (cerca de salida)" if puesto.zona == ZONA_EXPRESS else "Zona Larga Estadía"
        ruta.agregar_al_final(
            f"3. Camina por el pasillo central hasta la Fila {puesto.letra_fila} ({tipo_zona})."
        )
        ruta.agregar_al_final(
            f"4. Avanza hasta el Puesto #{puesto.columna + 1} -> Código {puesto.codigo}."
        )
        return ruta

    def localizar_vehiculo(self, criterio):
        """
        INNOVACIÓN 1: Búsqueda O(1) en Tabla Hash por placa o código de tiquete.
        """
        clave = criterio.strip().upper()
        if not clave:
            return {"ok": False, "mensaje": "Ingresa una placa o código de tiquete."}

        vehiculo = self.tabla_placas.buscar(clave)
        if vehiculo is None:
            vehiculo = self.tabla_tiquetes.buscar(clave)

        if vehiculo is None:
            return {"ok": False, "mensaje": f"No se encontró ningún vehículo parqueado con '{clave}'."}

        puesto = vehiculo.puesto_asignado
        ruta = self.construir_ruta_peatonal(puesto)
        return {
            "ok": True,
            "vehiculo": vehiculo,
            "puesto": puesto,
            "ruta": ruta.recorrer(),
        }

    def registrar_salida(self, criterio, minutos_simulados=None):
        clave = criterio.strip().upper()
        vehiculo = self.tabla_placas.buscar(clave) or self.tabla_tiquetes.buscar(clave)

        if vehiculo is None:
            return {"ok": False, "mensaje": f"No se encontró vehículo activo con '{clave}'."}

        puesto = vehiculo.puesto_asignado
        if minutos_simulados is not None:
            minutos = minutos_simulados
        else:
            delta = datetime.now() - vehiculo.hora_ingreso
            minutos = max(1, delta.total_seconds() / 60)

        total, detalle = calcular_tarifa(vehiculo, puesto, minutos)

        # Liberar puesto y reinsertarlo en el ABB
        puesto.estado = ESTADO_LIBRE
        puesto.vehiculo_actual = None
        self.arbol_disponibles.insertar(puesto.distancia_salida, puesto)

        # Retirar de las Tablas Hash
        self.tabla_placas.eliminar(vehiculo.placa)
        self.tabla_tiquetes.eliminar(vehiculo.codigo_tiquete)

        # Registrar factura en la Lista Enlazada de historial
        self.total_recaudado += total
        factura = {
            "tiquete": vehiculo.codigo_tiquete,
            "placa": vehiculo.placa,
            "categoria": vehiculo.etiqueta_categoria(),
            "puesto": puesto.codigo,
            "zona": puesto.zona,
            "minutos": int(round(minutos)),
            "total": total,
            "detalle": detalle,
            "hora_salida": datetime.now().strftime("%H:%M:%S"),
        }
        self.historial_facturas.agregar_al_final(factura)

        # Revisar si algún vehículo en Cola de Espera puede tomar el puesto liberado
        auto_asignado = self._procesar_cola_espera()

        return {
            "ok": True,
            "factura": factura,
            "auto_asignado": auto_asignado,
        }

    def _procesar_cola_espera(self):
        """
        INNOVACIÓN 3: Recorre la Cola usando exclusivamente desencolar() y encolar()
        para auto-asignar al primer vehículo compatible sin perder el orden FIFO.
        """
        total_en_cola = len(self.cola_espera)
        asignado_info = None

        for _ in range(total_en_cola):
            candidato = self.cola_espera.desencolar()
            if asignado_info is None:
                puesto = self._buscar_puesto_inteligente(candidato)
                if puesto is not None:
                    candidato.hora_ingreso = datetime.now()
                    self._asignar_vehiculo_a_puesto(candidato, puesto, registrar_en_pila=True)
                    asignado_info = (
                        f"Auto-asignación desde Cola: {candidato.placa} "
                        f"({candidato.codigo_tiquete}) ingresó al puesto {puesto.codigo}."
                    )
                    continue
            self.cola_espera.encolar(candidato)

        return asignado_info

    def alternar_mantenimiento(self, piso, fila, col):
        puesto = self.matrices[piso].obtener_celda(fila, col)
        if puesto.estado == ESTADO_OCUPADO:
            return {
                "ok": False,
                "mensaje": f"El puesto {puesto.codigo} está ocupado por {puesto.vehiculo_actual.placa}. Retira el vehículo primero.",
            }

        if puesto.estado == ESTADO_LIBRE:
            puesto.estado = ESTADO_MANTENIMIENTO
            self.arbol_disponibles.eliminar(puesto.distancia_salida)
            self.pila_acciones.apilar({
                "tipo": "MANTENIMIENTO_ON",
                "piso": piso,
                "fila": fila,
                "col": col,
                "descripcion": f"Bloqueo mantenimiento -> {puesto.codigo}",
            })
            return {"ok": True, "mensaje": f"Puesto {puesto.codigo} marcado en MANTENIMIENTO (removido del ABB)."}
        else:
            puesto.estado = ESTADO_LIBRE
            self.arbol_disponibles.insertar(puesto.distancia_salida, puesto)
            self.pila_acciones.apilar({
                "tipo": "MANTENIMIENTO_OFF",
                "piso": piso,
                "fila": fila,
                "col": col,
                "descripcion": f"Habilitación mantenimiento -> {puesto.codigo}",
            })
            auto = self._procesar_cola_espera()
            msg = f"Puesto {puesto.codigo} habilitado nuevamente (reinsertado en el ABB)."
            if auto:
                msg += f"\n{auto}"
            return {"ok": True, "mensaje": msg}

    def deshacer_ultima_accion(self):
        """
        INNOVACIÓN 3: Deshace la última operación registrada en la Pila (LIFO).
        """
        if self.pila_acciones.esta_vacia():
            return {"ok": False, "mensaje": "La pila de acciones está vacía. No hay nada que deshacer."}

        accion = self.pila_acciones.desapilar()
        tipo = accion["tipo"]

        if tipo == "INGRESO":
            placa = accion["placa"]
            vehiculo = self.tabla_placas.buscar(placa)
            if vehiculo is None:
                return {
                    "ok": False,
                    "mensaje": f"No se puede deshacer el ingreso de {placa} porque ya registró salida.",
                }
            puesto = vehiculo.puesto_asignado
            puesto.estado = ESTADO_LIBRE
            puesto.vehiculo_actual = None
            self.arbol_disponibles.insertar(puesto.distancia_salida, puesto)
            self.tabla_placas.eliminar(vehiculo.placa)
            self.tabla_tiquetes.eliminar(vehiculo.codigo_tiquete)
            return {
                "ok": True,
                "mensaje": f"Deshecho (Pila LIFO): se revirtió el ingreso de {placa} en {puesto.codigo}.",
            }

        puesto = self.matrices[accion["piso"]].obtener_celda(accion["fila"], accion["col"])
        if tipo == "MANTENIMIENTO_ON":
            if puesto.estado == ESTADO_MANTENIMIENTO:
                puesto.estado = ESTADO_LIBRE
                self.arbol_disponibles.insertar(puesto.distancia_salida, puesto)
                return {"ok": True, "mensaje": f"Deshecho (Pila LIFO): {puesto.codigo} vuelve a estar LIBRE."}
            return {"ok": False, "mensaje": f"El puesto {puesto.codigo} ya cambió de estado."}

        if tipo == "MANTENIMIENTO_OFF":
            if puesto.estado == ESTADO_LIBRE:
                puesto.estado = ESTADO_MANTENIMIENTO
                self.arbol_disponibles.eliminar(puesto.distancia_salida)
                return {"ok": True, "mensaje": f"Deshecho (Pila LIFO): {puesto.codigo} vuelve a MANTENIMIENTO."}
            return {"ok": False, "mensaje": f"No se puede volver a bloquear {puesto.codigo} porque ahora está ocupado."}

        return {"ok": False, "mensaje": "Acción no reversible."}

    def obtener_estadisticas(self):
        libres = ocupados = mantenimiento = 0
        for piso in (1, 2):
            for p in self.matrices[piso].todos_los_puestos():
                if p.estado == ESTADO_LIBRE:
                    libres += 1
                elif p.estado == ESTADO_OCUPADO:
                    ocupados += 1
                else:
                    mantenimiento += 1
        return {
            "libres": libres,
            "ocupados": ocupados,
            "mantenimiento": mantenimiento,
            "en_cola": len(self.cola_espera),
            "en_abb": len(self.arbol_disponibles),
            "recaudado": self.total_recaudado,
        }