# Sistema de Parqueadero Inteligente 24/7

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![GUI](https://img.shields.io/badge/Interfaz-Tkinter-green)
![Curso](https://img.shields.io/badge/Estructuras%20de%20Datos-G8F0054-orange)
![Universidad](https://img.shields.io/badge/Universidad%20de%20Caldas-Sistemas%20e%20Inform%C3%A1tica-003366)

Sistema de gestión integral para un parqueadero automatizado de **2 pisos y 80 espacios (24/7)**, desarrollado en **Python** con interfaz gráfica interactiva en **Tkinter**. El proyecto implementa **desde cero las 6 estructuras de datos fundamentales** (Árboles Binarios de Búsqueda recursivos, Tablas Hash, Matrices, Listas Enlazadas, Colas FIFO y Pilas LIFO) articuladas con **3 factores innovadores** orientados a resolver problemas reales de congestión, orientación del usuario y control operativo.

---

## Tabla de Contenidos

1. [Contexto Académico](#contexto-académico)
2. [Factores Innovadores](#factores-innovadores)
3. [Distribución de Espacios y Reglas de Negocio](#distribución-de-espacios-y-reglas-de-negocio)
4. [Reglas de Tarifación y Penalizaciones](#reglas-de-tarifación-y-penalizaciones)
5. [Estructuras de Datos Implementadas](#estructuras-de-datos-implementadas)
6. [Arquitectura del Proyecto](#arquitectura-del-proyecto)
7. [Requisitos e Instalación](#requisitos-e-instalación)
8. [Guía de Uso e Interfaz Gráfica](#guía-de-uso-e-interfaz-gráfica)
9. [Guion de Pruebas y Sustentación](#guion-de-pruebas-y-sustentación)
10. [Mejoras Futuras](#mejoras-futuras)
11. [Autores y Licencia](#autores-y-licencia)

---

## Contexto Académico

* **Institución:** Universidad de Caldas — Departamento de Sistemas e Informática
* **Asignatura:** Estructuras de Datos (`G8F0054` — PIAA Versión 2)
* **Lenguaje:** Python (biblioteca estándar, sin dependencias externas)
* **Objetivo:** Aplicar estructuras de datos lineales y no lineales, funciones recursivas y algoritmos de búsqueda eficientes en la solución de un problema real de ingeniería de software.

---

## Factores Innovadores

### 1. Localizador de Vehículo con Mapa y Ruta Peatonal
* **Problema que resuelve:** En parqueaderos amplios o de varios niveles, los conductores suelen olvidar el piso o la fila donde estacionaron, perdiendo tiempo al salir.
* **Solución técnica:** Cada vehículo ingresado se indexa en dos **Tablas Hash** propias (`placa -> Vehiculo` y `codigo_tiquete -> Vehiculo`) para consultas en tiempo promedio $O(1)$. Al buscarlo, el sistema cambia automáticamente al piso correspondiente, resalta el puesto en la matriz visual y construye dinámicamente una **Lista Enlazada** con la ruta paso a paso desde el acceso peatonal hasta el vehículo.

### 2. Asignación Inteligente por Tamaño y Tiempo de Estadía (Express vs. Larga Estadía)
* **Problema que resuelve:** El estacionamiento sin criterio genera trancones internos cuando vehículos de corta estadía quedan bloqueados al fondo o lejos de la salida.
* **Solución técnica:** Todos los puestos libres se indexan en un **Árbol Binario de Búsqueda (ABB)** ordenado por un puntaje único de distancia a la salida:
  $$\text{distancia\_salida} = (\text{piso} \times 1000) + (\text{fila} \times 100) + (\text{columna} + 1)$$
  * **Parada Express ($\le 15$ min) / Normal:** recorrido recursivo **InOrden** para asignar el puesto compatible **más cercano** a la salida.
  * **Larga Estadía ($> 3$ horas):** recorrido recursivo **InOrden inverso** para asignar el puesto compatible **más lejano**, dejando libres las zonas frontales.
  * **Restricción de altura:** las camionetas/SUV son filtradas automáticamente hacia el **Piso 1**.

### 3. Gestión Activa de Saturación (Cola de Espera Auto-Asignable) + Auditoría "Deshacer" (Pila LIFO)
* **Problema que resuelve:** Cuando una zona específica (ej. Motos Express o Piso 1 para SUV) se llena, se genera desorden en portería. Además, los errores de digitación o bloqueos accidentales del operario requieren corrección inmediata.
* **Solución técnica:**
  * **Cola de Espera (`FIFO`):** los vehículos sin cupo compatible se encolan automáticamente. En cuanto se libera o habilita un espacio compatible, el sistema recorre la cola respetando el orden estricto de llegada y ejecuta la **auto-asignación**.
  * **Pila de Auditoría (`LIFO`):** registra cada ingreso y cambio de mantenimiento, habilitando un botón de **Deshacer (Undo)** que revierte la última acción de forma segura y sincronizada con el ABB y las matrices.

---

## Distribución de Espacios y Reglas de Negocio

El parqueadero cuenta con **80 puestos totales** organizados en **2 matrices de $4 \times 10$** (50 automóviles y 30 motocicletas):

| Piso | Fila | Cantidad | Tipo de Vehículo | Zona | Restricción / Característica |
| :--- | :---: | :---: | :--- | :--- | :--- |
| **Piso 1** | A | 10 | Carro | **Express** | Más cercano a la salida a calle; apto para SUV |
| **Piso 1** | B | 10 | Moto | **Express** | Salida rápida directa a calle |
| **Piso 1** | C y D | 20 | Carro | Normal | Apto para **Camionetas / SUV** (techo alto) |
| **Piso 2** | A y B | 20 | Carro | Normal | Solo automóvil estándar (restricción de altura) |
| **Piso 2** | C y D | 20 | Moto | Normal | Zona exclusiva de motos de larga estadía |

### Gestión de Mantenimiento (4.º Estado)
El administrador puede hacer clic sobre cualquier celda libre en la interfaz para marcarla como **Fuera de Servicio / Mantenimiento**. Al hacerlo, el puesto se **elimina del ABB** para que el algoritmo de asignación lo ignore temporalmente. Al rehabilitarlo, el nodo se reinserta en el árbol y se verifica la Cola de Espera.

---

## Reglas de Tarifación y Penalizaciones

El horario de operación es **24/7** y el sistema incluye un **simulador de minutos** en la ventana de salida para facilitar la validación de todos los escenarios de cobro:

| Tipo de Vehículo | Modalidad / Zona | Tarifa Base | Regla de Tolerancia / Penalización |
| :--- | :--- | :--- | :--- |
| **Carro** | Normal | `$3.500` / hora | Tolerancia de 15 min: si supera `1:15:00` ($75$ min) se cobran **2 horas** (`$7.000`), y así sucesivamente cada hora adicional. |
| **Moto** | Normal | `$2.000` / hora | Misma regla de tolerancia de 15 min por hora (`> 75` min = 2 horas = `$4.000`). |
| **Carro** | **Express** ($\le 15$ min) | `$1.500` | Si supera los $15$ minutos pierde el beneficio Express y se cobra tarifa normal de 1 hora (`$3.500`), escalando si supera `1:15:00`. |
| **Moto** | **Express** ($\le 15$ min) | `$800` | Si supera los $15$ minutos pierde el beneficio Express y se cobra tarifa normal de 1 hora (`$2.000`), escalando si supera `1:15:00`. |

---

## Estructuras de Datos Implementadas

Todas las estructuras fueron construidas mediante **clases propias en `estructuras.py`** sin depender de implementaciones ocultas para su lógica central:

| Estructura | Clase Propia | Implementación Interna | Rol en el Sistema | Complejidad Clave |
| :--- | :--- | :--- | :--- | :--- |
| **Árboles (ABB)** | `ArbolBinarioBusqueda` | Nodos enlazados (`NodoABB`) con inserción, búsqueda, eliminación y recorridos **recursivos** (InOrden e InOrden inverso). | Índice dinámico de puestos libres ordenados por cercanía a la salida. | $O(\log n)$ promedio / $O(n)$ peor caso |
| **Diccionarios (Tabla Hash)** | `TablaHash` | Función hash polinomial ($h = (h \cdot 31 + c) \bmod M$, $M=101$) con encadenamiento separado. | Localización inmediata por placa y por código de tiquete (`TK-XXXX`). | $O(1)$ promedio en búsqueda, inserción y borrado |
| **Matrices** | `MatrizParqueadero` | Arreglo bidimensional $4 \times 10$ por cada piso. | Representación espacial de ambos pisos sincronizada con los botones de la GUI. | $O(1)$ acceso directo por $(f, c)$ |
| **Listas** | `ListaEnlazada` | Lista simplemente enlazada con punteros `cabeza` y `cola`. | Generación de pasos de la ruta peatonal e historial acumulado de facturas. | $O(1)$ inserción al final / $O(n)$ recorrido |
| **Colas (FIFO)** | `Cola` | Nodos enlazados con punteros `frente` y `final`. | Cola de espera en portería con auto-asignación justa al liberarse un cupo. | $O(1)$ encolar y desencolar |
| **Pilas (LIFO)** | `Pila` | Nodos enlazados con puntero `tope`. | Historial de auditoría y función **Deshacer (Undo)** de operaciones recientes. | $O(1)$ apilar y desapilar |

---

## Arquitectura del Proyecto

```text
parqueadero_inteligente/
├── estructuras.py   # Implementación desde cero de las 6 estructuras de datos
├── modelos.py       # Clases de dominio (Puesto, Vehiculo), constantes y motor de tarifas
├── sistema.py       # Controlador central: integra las 6 estructuras y las 3 innovaciones
├── main.py          # Interfaz gráfica interactiva en Tkinter (mapa 2 pisos + paneles)
└── README.md        # Documentación general del proyecto
```

### Separación de responsabilidades
* **`estructuras.py`:** capa pura de estructuras de datos genéricas y reutilizables.
* **`modelos.py`:** entidades del negocio y lógica matemática pura de facturación (`calcular_tarifa`).
* **`sistema.py`:** orquestador sin acoplamiento gráfico; permite probar o migrar la interfaz sin modificar la lógica.
* **`main.py`:** capa de presentación con actualización reactiva de estados, colores, estadísticas e inspección del ABB en tiempo real.

---

## Requisitos e Instalación

### Prerrequisitos
* **Python 3.8 o superior** instalado en tu sistema.
* **Tkinter** (incluido por defecto en las instalaciones oficiales de Python para Windows y macOS).

> **Nota para usuarios de Linux (Ubuntu/Debian):** si al ejecutar aparece un error indicando que falta el módulo `tkinter`, instálalo con:
> ```bash
> sudo apt-get update && sudo apt-get install python3-tk
> ```

### Clonar y ejecutar

1. Clona este repositorio en tu equipo:
   ```bash
   git clone https://github.com/<tu-usuario>/parqueadero-inteligente.git
   ```
2. Ingresa al directorio del proyecto:
   ```bash
   cd parqueadero-inteligente
   ```
3. Ejecuta la aplicación:
   ```bash
   python main.py
   ```
   *(En sistemas donde Python 3 se invoque explícitamente, utiliza `python3 main.py`).*

---

## Guía de Uso e Interfaz Gráfica

### Código de Colores del Mapa Interactivo
* **Verde:** Puesto libre en zona **Normal**.
* **Azul:** Puesto libre en zona **Express** (Piso 1, filas A y B).
* **Rojo:** Puesto **Ocupado** (muestra la placa del vehículo; al hacer clic abre sus datos).
* **Amarillo / Ámbar:** Puesto en **Mantenimiento** (excluido temporalmente del ABB).
* **Morado:** Puesto **Localizado** actualmente desde el buscador.

### Pestañas de Control
1. **`1. Ingreso (ABB)`:** registra placa, tipo/tamaño del vehículo y tiempo estimado de estadía. Incluye un botón de **Cargar Datos de Prueba** para poblar rápidamente ambos pisos.
2. **`2. Localizador / Salida`:** busca vehículos por placa o código de tiquete (`TK-0001`), resalta su posición en el mapa, despliega la ruta peatonal y procesa la salida con opción de **simular minutos**.
3. **`3. Cola / Pila / ABB`:** visualiza en vivo la Cola de Espera, la Pila de Auditoría (con botón **Deshacer Última Acción**), el Historial de Facturas y un visor del **Recorrido InOrden del ABB**.

---

## Guion de Pruebas y Sustentación

Para verificar todas las estructuras y reglas de negocio durante una demostración:

1. **Asignación inteligente (ABB + Matrices):** pulsa **Cargar Datos de Prueba**. Observa cómo los vehículos Express se asignan al inicio del Piso 1, los carros estándar de Larga Estadía al fondo del Piso 2 y las camionetas SUV permanecen restringidas al Piso 1.
2. **Verificación del Árbol:** abre la pestaña `3. Cola / Pila / ABB` y haz clic en **Inspeccionar Recorrido InOrden del ABB** para comprobar que los puestos ocupados fueron eliminados y los disponibles permanecen ordenados por cercanía.
3. **Localizador (Tabla Hash + Lista Enlazada):** busca `LRG401` o su tiquete en la pestaña `2. Localizador / Salida`. El mapa saltará al Piso 2, iluminará el puesto en morado y listará la ruta peatonal.
4. **Cálculo de tarifas y penalizaciones:**
   * Salida de `EXP101` (Carro Express) con `12` min -> `$1.500`.
   * Salida de `EXP102` (Carro Express) con `18` min -> `$3.500` (penalización por superar 15 min).
   * Salida de `LRG401` (Carro Normal) con `76` min (`1:16:00`) -> `$7.000` (cobro de 2 horas al superar `1:15:00`).
5. **Mantenimiento y Deshacer (Pila LIFO):** haz clic en una celda libre para bloquearla en mantenimiento y luego presiona **Deshacer Última Acción** en la pestaña 3 para revertir el cambio.
6. **Cola de Espera con auto-asignación (FIFO):** llena o bloquea los 10 puestos de `Motos Express` (Piso 1, Fila B), ingresa una moto Express adicional para enviarla a la Cola de Espera y libera luego un puesto de la Fila B para ver su ingreso automático.

---

## Mejoras Futuras

* Persistencia de estado e historial de facturación en archivos `JSON` o base de datos `SQLite`.
* Balanceo automático del árbol migrando el ABB a un **Árbol AVL** (cubierto en el Tema 2 del PIAA) para garantizar $O(\log n)$ incluso en el peor caso.
* Generación de tiquetes imprimibles con código QR y exportación de reportes financieros a CSV/Excel.
* Modelado de rutas internas del parqueadero mediante **Grafos** y algoritmo de Dijkstra para calcular trayectorias con múltiples salidas peatonales.

---

## Autores y Licencia

* **Desarrollado por:** *[Agrega aquí tu nombre y el de tus compañeros de equipo]*
* **Curso:** Estructuras de Datos (`G8F0054`) — Universidad de Caldas

Este proyecto se distribuye bajo la licencia **MIT**, lo que permite su uso, estudio y modificación con fines académicos y educativos.