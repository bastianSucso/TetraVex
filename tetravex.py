from __future__ import annotations

import random
import time

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from kanren import eq, lall, membero, run, var
from kanren.constraints import neq

Pieza = tuple[int, int, int, int]
PiezaIndexada = tuple[int, int, int, int, int]
TableroLineal = tuple[Pieza, ...]


def es_pieza(valor: object) -> bool:
    if (not isinstance(valor, (tuple, list))) or len(valor) != 4: #Recibe valor, en isintance, evalua si valor es tupla o lista y si esta es distinta de 4
        return False
    return all(isinstance(lado, int) for lado in valor) #evalúa cada lado del valor, y si lado es de tipo   int devuelve true. 


def tamano_tablero_desde_piezas(piezas: tuple[Pieza, ...]) -> int:
    cantidad = len(piezas)
    n = int(cantidad**0.5)
    if n * n != cantidad:
        raise ValueError("La cantidad de piezas no forma un tablero cuadrado.")
    return n


def normalizar_entrada(puzzle: object) -> tuple[tuple[Pieza, ...], int]:
    if not isinstance(puzzle, (tuple, list)) or not puzzle:    #Si puzzle es tupla, o lista -> true (+not = false), o es [], (), "", 0, None -> False
        raise ValueError("El puzzle debe ser una lista/tupla no vacia.")

    if all(es_pieza(elem) for elem in puzzle): #Aplica es_pieza a cada elemento para detectar si la entrada ya es plana
        piezas = tuple(tuple(int(v) for v in pieza) for pieza in puzzle)  # type: ignore[arg-type]
        return piezas, tamano_tablero_desde_piezas(piezas)

    if not all(isinstance(fila, (tuple, list)) for fila in puzzle):
        raise ValueError("Entrada invalida: use puzzle plano o anidado n x n.")

    filas = tuple(puzzle)
    n = len(filas)
    if n == 0:
        raise ValueError("El puzzle anidado no puede estar vacio.")

    piezas_planas: list[Pieza] = []
    for fila in filas:
        if not isinstance(fila, (tuple, list)) or len(fila) != n:
            raise ValueError("El puzzle anidado debe tener forma n x n.")
        for pieza in fila:
            if not es_pieza(pieza):
                raise ValueError("Cada pieza debe ser una tupla/lista de 4 enteros.")
            piezas_planas.append(tuple(int(v) for v in pieza))

    piezas = tuple(piezas_planas)
    tamano_deducido = tamano_tablero_desde_piezas(piezas)
    if tamano_deducido != n:
        raise ValueError("Inconsistencia en dimensiones del puzzle anidado.")
    return piezas, n


def formatear_tablero(tablero: TableroLineal, n: int) -> str:
    lineas: list[str] = []
    for fila in range(n):
        inicio = fila * n
        termino = inicio + n
        fila_piezas = tablero[inicio:termino]
        lineas.append(" ".join(str(pieza) for pieza in fila_piezas))
    return "\n".join(lineas)


def indexar_piezas(piezas: tuple[Pieza, ...]) -> tuple[PiezaIndexada, ...]:
    return tuple((idx, pieza[0], pieza[1], pieza[2], pieza[3]) for idx, pieza in enumerate(piezas))


def lados_pieza(
    pieza: object,
    izquierda: object,
    derecha: object,
    superior: object,
    inferior: object,
):
    identificador = var()
    return eq((identificador, izquierda, derecha, superior, inferior), pieza)


def coinciden_horizontal(pieza_izquierda: object, pieza_derecha: object):
    derecha_izquierda = var()
    izquierda_derecha = var()
    return lall(
        lados_pieza(pieza_izquierda, var(), derecha_izquierda, var(), var()),
        lados_pieza(pieza_derecha, izquierda_derecha, var(), var(), var()),
        eq(derecha_izquierda, izquierda_derecha),
    )


def coinciden_vertical(pieza_superior: object, pieza_inferior: object):
    inferior_superior = var()
    superior_inferior = var()
    return lall(
        lados_pieza(pieza_superior, var(), var(), var(), inferior_superior),
        lados_pieza(pieza_inferior, var(), var(), superior_inferior, var()),
        eq(inferior_superior, superior_inferior),
    )


def restricciones_adyacencia(celdas_tablero: tuple[object, ...], n: int):
    metas: list[object] = []
    for posicion, celda in enumerate(celdas_tablero):
        fila, columna = divmod(posicion, n)

        if columna > 0:
            izquierda = celdas_tablero[posicion - 1]
            metas.append(coinciden_horizontal(izquierda, celda))

        if fila > 0:
            superior = celdas_tablero[posicion - n]
            metas.append(coinciden_vertical(superior, celda))

    return lall(*metas)


def dominio_celdas(celdas_tablero: tuple[object, ...], piezas_indexadas: tuple[PiezaIndexada, ...]):
    return lall(*(membero(celda, piezas_indexadas) for celda in celdas_tablero))


def diferencias_celdas(celdas_tablero: tuple[object, ...]):
    total_celdas = len(celdas_tablero)
    return lall(
        *(neq(celdas_tablero[i], celdas_tablero[j]) for i in range(total_celdas) for j in range(i + 1, total_celdas))
    )


def tetravexproblem(
    celdas_tablero: tuple[object, ...],
    piezas_indexadas: tuple[PiezaIndexada, ...],
    n: int,
):
    return lall(
        restricciones_adyacencia(celdas_tablero, n),
        dominio_celdas(celdas_tablero, piezas_indexadas),
        diferencias_celdas(celdas_tablero),
    )


def resolver_con_minikanren(puzzle: object) -> TableroLineal | None:
    piezas, n = normalizar_entrada(puzzle)
    piezas_indexadas = indexar_piezas(piezas)
    celdas_tablero = tuple(var() for _ in range(n * n))

    soluciones = run(1, celdas_tablero, tetravexproblem(celdas_tablero, piezas_indexadas, n))
    if not soluciones:
        return None

    solucion_indexada = soluciones[0]
    solucion = tuple(
        (pieza[1], pieza[2], pieza[3], pieza[4])
        for pieza in solucion_indexada
    )
    return solucion


def ejemplo() -> None:
    puzzle = (
        ((1,9,2,2),(1,9,4,9),(6,8,9,7)),
        ((9,9,2,9),(0,6,9,5),(0,1,5,4)),
        ((4,0,7,7),(5,1,4,7),(7,0,6,4))
        )

    piezas, n = normalizar_entrada(puzzle)
    solucion = resolver_con_minikanren(piezas)

    if solucion is None:
        print("No se encontro solucion.")
        return

    print("Solucion encontrada:\n")
    print(formatear_tablero(solucion, n))


def generar_tablero_resuelto(
    n: int,
    maximo_digito: int = 9,
    semilla: int | None = None,
) -> TableroLineal:
    generador = random.Random(semilla)
    tablero: list[list[Pieza | None]] = [[None] * n for _ in range(n)]
    inferiores_previos: list[int | None] = [None] * n

    for fila in range(n):
        derecha_previa: int | None = None
        for columna in range(n):
            izquierda = derecha_previa if columna > 0 else generador.randint(0, maximo_digito)
            superior = (
                inferiores_previos[columna]
                if fila > 0
                else generador.randint(0, maximo_digito)
            )
            derecha = generador.randint(0, maximo_digito)
            inferior = generador.randint(0, maximo_digito)

            pieza: Pieza = (int(izquierda), int(derecha), int(superior), int(inferior))
            tablero[fila][columna] = pieza

            derecha_previa = derecha
            inferiores_previos[columna] = inferior

    return tuple(pieza for fila in tablero for pieza in fila if pieza is not None)


def mezclar_puzzle_desde_solucion(
    solucion: TableroLineal,
    semilla: int | None = None,
) -> TableroLineal:
    generador = random.Random(semilla)
    piezas = list(solucion)
    generador.shuffle(piezas)
    return tuple(piezas)


def benchmark_tiempos(
    tamanos: tuple[int, ...] = (2, 3, 4),
    repeticiones: int = 3,
    graficar: bool = False,
    ruta_grafico: str = "benchmark_tetravex.png",
) -> None:
    if any(not isinstance(n, int) for n in tamanos):
        raise ValueError("Las dimensiones del tablero deben ser enteros.")

    tiempos_promedio: list[float] = []

    for n in tamanos:
        tiempos: list[float] = []
        for intento in range(repeticiones):
            resuelto = generar_tablero_resuelto(n, maximo_digito=9, semilla=1000 + n * 10 + intento)
            puzzle = mezclar_puzzle_desde_solucion(resuelto, semilla=2000 + n * 10 + intento)

            inicio = time.perf_counter()
            _ = resolver_con_minikanren(puzzle)
            fin = time.perf_counter()

            tiempos.append(fin - inicio)

        promedio = sum(tiempos) / len(tiempos)
        tiempos_promedio.append(promedio)
        print(f"{n}x{n}: promedio {promedio:.6f} segundos ({repeticiones} corridas)")

    plt.figure(figsize=(8, 5))
    plt.plot(tamanos, tiempos_promedio, marker="o", linewidth=1.8)
    plt.scatter(tamanos, tiempos_promedio, s=35, zorder=3)
    ax = plt.gca()

    margen_izquierdo = min(tamanos) - 0.35
    margen_derecho = max(tamanos) + 0.35
    ax.set_xlim(margen_izquierdo, margen_derecho)
    ax.set_xticks(list(tamanos))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda valor, _pos: f"{int(valor)}"))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda valor, _pos: f"{valor:.3f}"))

    for n, tiempo in zip(tamanos, tiempos_promedio):
        ax.hlines(y=tiempo, xmin=margen_izquierdo, xmax=n, colors="gray", linestyles="--", linewidth=0.8, alpha=0.65)
        ax.annotate(
            f"{tiempo:.6f}",
            xy=(n, tiempo),
            xytext=(6, 6),
            textcoords="offset points",
            fontsize=8,
        )

    plt.xlabel("Dimension del tablero (n)")
    plt.ylabel("Tiempo promedio de resolucion (segundos)")
    plt.title("Benchmark TetraVex con miniKanren")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(ruta_grafico)

    if graficar:
        plt.show()
    else:
        plt.close()

    print(f"Grafico guardado en: {ruta_grafico}")


if __name__ == "__main__":
    ejemplo()
    print("\n--- Benchmark ---")
    benchmark_tiempos()
