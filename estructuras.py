"""
Implementación completa de las 6 estructuras de datos requeridas:
1. Lista Enlazada (ListaEnlazada)
2. Pila (Pila - LIFO)
3. Cola (Cola - FIFO)
4. Diccionario / Tabla Hash (TablaHash)
5. Árbol Binario de Búsqueda con métodos recursivos (ArbolBinarioBusqueda)
6. Matriz 2D por piso (MatrizParqueadero)
"""


# ==============================================================================
# 1. LISTA ENLAZADA SIMPLE
# ==============================================================================
class NodoLista:
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None


class ListaEnlazada:
    def __init__(self):
        self.cabeza = None
        self.cola = None
        self._tamano = 0

    def esta_vacia(self):
        return self.cabeza is None

    def agregar_al_final(self, dato):
        nuevo = NodoLista(dato)
        if self.esta_vacia():
            self.cabeza = self.cola = nuevo
        else:
            self.cola.siguiente = nuevo
            self.cola = nuevo
        self._tamano += 1

    def agregar_al_inicio(self, dato):
        nuevo = NodoLista(dato)
        if self.esta_vacia():
            self.cabeza = self.cola = nuevo
        else:
            nuevo.siguiente = self.cabeza
            self.cabeza = nuevo
        self._tamano += 1

    def recorrer(self):
        """Devuelve los elementos en orden para visualización o reporte."""
        elementos = []
        actual = self.cabeza
        while actual is not None:
            elementos.append(actual.dato)
            actual = actual.siguiente
        return elementos

    def __len__(self):
        return self._tamano


# ==============================================================================
# 2. PILA (STACK - LIFO)
# ==============================================================================
class Pila:
    def __init__(self):
        self._tope = None
        self._tamano = 0

    def esta_vacia(self):
        return self._tope is None

    def apilar(self, dato):
        nuevo = NodoLista(dato)
        nuevo.siguiente = self._tope
        self._tope = nuevo
        self._tamano += 1

    def desapilar(self):
        if self.esta_vacia():
            return None
        dato = self._tope.dato
        self._tope = self._tope.siguiente
        self._tamano -= 1
        return dato

    def ver_tope(self):
        return None if self.esta_vacia() else self._tope.dato

    def listar_elementos(self):
        """Retorna los elementos desde el tope hacia la base."""
        elementos = []
        actual = self._tope
        while actual is not None:
            elementos.append(actual.dato)
            actual = actual.siguiente
        return elementos

    def __len__(self):
        return self._tamano


# ==============================================================================
# 3. COLA (QUEUE - FIFO)
# ==============================================================================
class Cola:
    def __init__(self):
        self._frente = None
        self._final = None
        self._tamano = 0

    def esta_vacia(self):
        return self._frente is None

    def encolar(self, dato):
        nuevo = NodoLista(dato)
        if self.esta_vacia():
            self._frente = self._final = nuevo
        else:
            self._final.siguiente = nuevo
            self._final = nuevo
        self._tamano += 1

    def desencolar(self):
        if self.esta_vacia():
            return None
        dato = self._frente.dato
        self._frente = self._frente.siguiente
        if self._frente is None:
            self._final = None
        self._tamano -= 1
        return dato

    def ver_frente(self):
        return None if self.esta_vacia() else self._frente.dato

    def listar_elementos(self):
        elementos = []
        actual = self._frente
        while actual is not None:
            elementos.append(actual.dato)
            actual = actual.siguiente
        return elementos

    def __len__(self):
        return self._tamano


# ==============================================================================
# 4. DICCIONARIO / TABLA HASH (ENCADENAMIENTO SEPARADO)
# ==============================================================================
class TablaHash:
    def __init__(self, capacidad=101):
        # Número primo para distribuir mejor las claves y minimizar colisiones
        self.capacidad = capacidad
        self._cubetas = [[] for _ in range(capacidad)]
        self._tamano = 0

    def _hash(self, clave):
        """Función hash polinomial para cadenas (placas o códigos de tiquete)."""
        clave_str = str(clave).upper()
        h = 0
        for caracter in clave_str:
            h = (h * 31 + ord(caracter)) % self.capacidad
        return h

    def insertar(self, clave, valor):
        clave_norm = str(clave).upper()
        indice = self._hash(clave_norm)
        cubeta = self._cubetas[indice]
        for par in cubeta:
            if par[0] == clave_norm:
                par[1] = valor
                return
        cubeta.append([clave_norm, valor])
        self._tamano += 1

    def buscar(self, clave):
        clave_norm = str(clave).upper()
        indice = self._hash(clave_norm)
        for k, v in self._cubetas[indice]:
            if k == clave_norm:
                return v
        return None

    def eliminar(self, clave):
        clave_norm = str(clave).upper()
        indice = self._hash(clave_norm)
        cubeta = self._cubetas[indice]
        for i, (k, _) in enumerate(cubeta):
            if k == clave_norm:
                cubeta.pop(i)
                self._tamano -= 1
                return True
        return False

    def contiene(self, clave):
        return self.buscar(clave) is not None

    def valores(self):
        resultado = []
        for cubeta in self._cubetas:
            for _, v in cubeta:
                resultado.append(v)
        return resultado

    def __len__(self):
        return self._tamano


# ==============================================================================
# 5. ÁRBOL BINARIO DE BÚSQUEDA (ABB CON OPERACIONES RECURSIVAS)
# ==============================================================================
class NodoABB:
    def __init__(self, clave, valor):
        self.clave = clave      # Puntaje de cercanía a la salida (menor = más cerca)
        self.valor = valor      # Objeto Puesto
        self.izq = None
        self.der = None


class ArbolBinarioBusqueda:
    def __init__(self):
        self.raiz = None
        self._tamano = 0

    def insertar(self, clave, valor):
        if self.buscar(clave) is None:
            self._tamano += 1
        self.raiz = self._insertar_rec(self.raiz, clave, valor)

    def _insertar_rec(self, nodo, clave, valor):
        if nodo is None:
            return NodoABB(clave, valor)
        if clave < nodo.clave:
            nodo.izq = self._insertar_rec(nodo.izq, clave, valor)
        elif clave > nodo.clave:
            nodo.der = self._insertar_rec(nodo.der, clave, valor)
        else:
            nodo.valor = valor
        return nodo

    def buscar(self, clave):
        return self._buscar_rec(self.raiz, clave)

    def _buscar_rec(self, nodo, clave):
        if nodo is None:
            return None
        if clave == nodo.clave:
            return nodo.valor
        if clave < nodo.clave:
            return self._buscar_rec(nodo.izq, clave)
        return self._buscar_rec(nodo.der, clave)

    def eliminar(self, clave):
        if self.buscar(clave) is None:
            return False
        self.raiz = self._eliminar_rec(self.raiz, clave)
        self._tamano -= 1
        return True

    def _eliminar_rec(self, nodo, clave):
        if nodo is None:
            return None
        if clave < nodo.clave:
            nodo.izq = self._eliminar_rec(nodo.izq, clave)
        elif clave > nodo.clave:
            nodo.der = self._eliminar_rec(nodo.der, clave)
        else:
            # Caso 1 y 2: nodo hoja o con un solo hijo
            if nodo.izq is None:
                return nodo.der
            if nodo.der is None:
                return nodo.izq
            # Caso 3: dos hijos -> reemplazar con el sucesor InOrden (mínimo derecho)
            sucesor = self._min_nodo(nodo.der)
            nodo.clave = sucesor.clave
            nodo.valor = sucesor.valor
            nodo.der = self._eliminar_rec(nodo.der, sucesor.clave)
        return nodo

    def _min_nodo(self, nodo):
        actual = nodo
        while actual.izq is not None:
            actual = actual.izq
        return actual

    def buscar_primero_que_cumpla(self, condicion, inverso=False):
        """
        Recorrido recursivo InOrden (inverso=False -> más cercano a la salida)
        o InOrden inverso (inverso=True -> más lejano de la salida).
        """
        return self._buscar_cond_rec(self.raiz, condicion, inverso)

    def _buscar_cond_rec(self, nodo, condicion, inverso):
        if nodo is None:
            return None
        primero = nodo.der if inverso else nodo.izq
        segundo = nodo.izq if inverso else nodo.der

        hallado = self._buscar_cond_rec(primero, condicion, inverso)
        if hallado is not None:
            return hallado
        if condicion(nodo.valor):
            return nodo.valor
        return self._buscar_cond_rec(segundo, condicion, inverso)

    def recorrido_inorden(self):
        resultado = []
        self._inorden_rec(self.raiz, resultado)
        return resultado

    def _inorden_rec(self, nodo, resultado):
        if nodo is not None:
            self._inorden_rec(nodo.izq, resultado)
            resultado.append((nodo.clave, nodo.valor))
            self._inorden_rec(nodo.der, resultado)

    def __len__(self):
        return self._tamano


# ==============================================================================
# 6. MATRIZ 2D DEL PARQUEADERO (UN PISO)
# ==============================================================================
class MatrizParqueadero:
    def __init__(self, piso, filas=4, columnas=10):
        self.piso = piso
        self.filas = filas
        self.columnas = columnas
        self._grid = [[None for _ in range(columnas)] for _ in range(filas)]

    def asignar_celda(self, fila, col, puesto):
        self._grid[fila][col] = puesto

    def obtener_celda(self, fila, col):
        return self._grid[fila][col]

    def todos_los_puestos(self):
        puestos = []
        for f in range(self.filas):
            for c in range(self.columnas):
                puestos.append(self._grid[f][c])
        return puestos