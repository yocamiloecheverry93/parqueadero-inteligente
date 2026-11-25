import math
from datetime import datetime

# Estados de un puesto en la matriz
ESTADO_LIBRE = "LIBRE"
ESTADO_OCUPADO = "OCUPADO"
ESTADO_MANTENIMIENTO = "MANTENIMIENTO"

# Zonas
ZONA_EXPRESS = "EXPRESS"
ZONA_NORMAL = "NORMAL"

# Categorías de vehículos
CAT_CARRO_ESTANDAR = "CARRO_ESTANDAR"
CAT_CAMIONETA_SUV = "CAMIONETA_SUV"
CAT_MOTO = "MOTO"

# Modalidades de estadía al ingresar
MOD_EXPRESS = "EXPRESS"      # <= 15 minutos
MOD_NORMAL = "NORMAL"        # 1 a 3 horas
MOD_LARGA = "LARGA"          # Más de 3 horas / todo el día

LETRAS_FILA = ["A", "B", "C", "D"]


class Puesto:
    def __init__(self, piso, fila, columna, zona, tipo_base, permite_suv):
        self.piso = piso                  # 1 o 2
        self.fila = fila                  # 0..3 (A..D)
        self.columna = columna            # 0..9 (1..10)
        self.zona = zona                  # EXPRESS o NORMAL
        self.tipo_base = tipo_base        # CARRO o MOTO
        self.permite_suv = permite_suv    # True solo en Piso 1 para carros
        self.estado = ESTADO_LIBRE
        self.vehiculo_actual = None

        self.letra_fila = LETRAS_FILA[fila]
        self.codigo = f"P{piso}-{self.letra_fila}{columna + 1:02d}"
        # Clave única para el ABB: menor valor = más cerca de la salida a la calle
        self.distancia_salida = (piso * 1000) + (fila * 100) + (columna + 1)

    def __repr__(self):
        return f"Puesto({self.codigo}, {self.tipo_base}, {self.zona}, {self.estado})"


class Vehiculo:
    def __init__(self, placa, categoria, modalidad, codigo_tiquete):
        self.placa = placa.strip().upper()
        self.categoria = categoria
        self.tipo_base = "MOTO" if categoria == CAT_MOTO else "CARRO"
        self.modalidad = modalidad
        self.codigo_tiquete = codigo_tiquete
        self.hora_ingreso = datetime.now()
        self.puesto_asignado = None

    def etiqueta_categoria(self):
        nombres = {
            CAT_CARRO_ESTANDAR: "Automóvil Estándar",
            CAT_CAMIONETA_SUV: "Camioneta / SUV",
            CAT_MOTO: "Motocicleta",
        }
        return nombres.get(self.categoria, self.categoria)


def calcular_tarifa(vehiculo, puesto, minutos_totales):
    """
    Aplica las reglas oficiales de cobro:
    - Carro Normal: $3.500/h. Si supera 1:15:00 (75 min) cobra 2 horas (15 min tolerancia/hora).
    - Moto Normal:  $2.000/h. Misma tolerancia de 15 min por hora.
    - Express <= 15 min: Carro $1.500 | Moto $800.
    - Express > 15 min:  Se penaliza cobrando tarifa normal de 1 hora (o más si supera 1:15:00).
    """
    minutos = max(1, int(math.ceil(minutos_totales)))
    es_carro = vehiculo.tipo_base == "CARRO"
    tarifa_hora = 3500 if es_carro else 2000
    tarifa_express = 1500 if es_carro else 800

    # Caso 1: Estuvo en zona Express y respetó los 15 minutos
    if puesto.zona == ZONA_EXPRESS and minutos <= 15:
        return (
            tarifa_express,
            f"Tarifa Express ({minutos} min <= 15 min): ${tarifa_express:,}"
        )

    # Caso 2: Superó 15 min en zona Express o estuvo en zona Normal
    if minutos <= 75:
        horas_cobradas = 1
    else:
        # Supera 1:15:00 -> cobra 2 horas; cada 60 min adicionales suma 1 hora
        horas_cobradas = 1 + math.ceil((minutos - 75) / 60)

    total = horas_cobradas * tarifa_hora

    if puesto.zona == ZONA_EXPRESS:
        detalle = (
            f"Penalización Express ({minutos} min > 15 min): "
            f"se cobra como tarifa normal ({horas_cobradas} h x ${tarifa_hora:,}) = ${total:,}"
        )
    else:
        nota_tolerancia = " (superó 1:15:00)" if minutos > 75 else " (dentro de 1:15:00)"
        detalle = (
            f"Tarifa Normal {vehiculo.tipo_base} ({minutos} min{nota_tolerancia}): "
            f"{horas_cobradas} h x ${tarifa_hora:,} = ${total:,}"
        )

    return total, detalle