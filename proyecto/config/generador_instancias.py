from typing import Dict, Any, List, Optional
import random
from .taller_config import (
    TAREAS,
    PRECEDENCIAS,
    DURACIONES_BASE,
    OPERARIOS,
    OPERARIOS_APTOS,
    HORIZONTE,
)


CATEGORIAS_TAREAS: Dict[str, List[int]] = {
    "BLOQUE": list(range(1, 15)),
    "BIELAS": list(range(15, 20)),
    "CIGUENAL": list(range(20, 25)),
    "CULATA": list(range(25, 36)),
}

TAREA_A_CATEGORIA: Dict[int, str] = {}
for categoria, ids in CATEGORIAS_TAREAS.items():
    for tarea_id in ids:
        TAREA_A_CATEGORIA[tarea_id] = categoria


def generar_instancia(
    instancia_id: str,
    num_ot: int,
    min_tareas_por_ot: int = 3,
    max_tareas_por_ot: int = 7,
    variabilidad_duracion: float = 0.10,
    prob_falta_repuesto: float = 0.15,
    pesos_categorias: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """Genera una sola instancia válida para los algoritmos AG y SPT."""

    ot_list = list(range(1, num_ot + 1))
    mapeo_ot: Dict[int, List[int]] = {}
    tareas_a_programar: List[tuple[int, int]] = []
    repuestos_por_ot: Dict[int, List[int]] = {}

    tareas_disponibles = list(TAREAS.values())
    precedencias_instancia = _aplicar_precedencias_opcionales(PRECEDENCIAS)

    for ot in ot_list:
        cantidad = random.randint(min_tareas_por_ot, max_tareas_por_ot)
        tareas_ot = _seleccionar_tareas_validas(
            cantidad,
            tareas_disponibles,
            precedencias_instancia,
            pesos_categorias,
        )
        mapeo_ot[ot] = tareas_ot
        tareas_a_programar.extend((ot, tarea) for tarea in tareas_ot)
        repuestos_por_ot[ot] = [
            0 if random.random() < prob_falta_repuesto else 1 for _ in tareas_ot
        ]

    tiempos = _generar_duraciones_variadas(DURACIONES_BASE, variabilidad_duracion)

    return {
        "instancia_id": instancia_id,
        "OT": ot_list,
        "tareas_a_programar": tareas_a_programar,
        "mapeo_ot": mapeo_ot,
        "tiempos_procesamiento": tiempos,
        "prerequisitos": precedencias_instancia,
        "repuestos_por_ot": repuestos_por_ot,
        "operarios": OPERARIOS,
        "operarios_aptos": OPERARIOS_APTOS,
        "horizonte": HORIZONTE,
    }


def generar_batch_instancias(
    n: int,
    min_ot: int = 4,
    max_ot: int = 12,
    seed: int | None = None,
    pesos_categorias: Optional[Dict[str, float]] = None,
) -> List[Dict[str, Any]]:
    """Genera un conjunto de instancias aleatorias."""
    if seed is not None:
        random.seed(seed)

    batch = []
    for i in range(n):
        num_ot = random.randint(min_ot, max_ot)
        batch.append(
            generar_instancia(
                f"inst_{i}",
                num_ot,
                pesos_categorias=pesos_categorias,
            )
        )
    return batch


def _seleccionar_tareas_validas(
    cantidad: int,
    universo: List[int],
    precedencias: Dict[int, List[int]],
    pesos_categorias: Optional[Dict[str, float]] = None,
) -> List[int]:
    """Selecciona un subconjunto de tareas que respeta todas las precedencias."""
    seleccionadas: List[int] = []
    candidatos = universo.copy()
    random.shuffle(candidatos)

    while candidatos and len(seleccionadas) < cantidad:
        categoria = _seleccionar_categoria(candidatos, pesos_categorias)
        tarea = _seleccionar_candidato(candidatos, categoria)
        candidatos.remove(tarea)

        if _puede_agregarse(tarea, seleccionadas, precedencias):
            seleccionadas.append(tarea)

    seleccionadas.sort(
        key=lambda tarea: (
            len(precedencias.get(tarea, [])),
            tarea,
        )
    )
    return seleccionadas


def _puede_agregarse(tarea: int, seleccionadas: List[int], precedencias: Dict[int, List[int]]) -> bool:
    """Verifica que todas las precedencias de la tarea estén en la selección."""
    requeridas = precedencias.get(tarea, [])
    return all(req in seleccionadas for req in requeridas)


def _generar_duraciones_variadas(
    duraciones_base: Dict[int, int],
    variabilidad: float,
) -> Dict[int, int]:
    """Aplica variabilidad aleatoria a las duraciones base."""
    tiempos = {}
    for tarea_id, base in duraciones_base.items():
        factor = random.uniform(1 - variabilidad, 1 + variabilidad)
        tiempos[tarea_id] = max(1, int(round(base * factor)))
    return tiempos


def _aplicar_precedencias_opcionales(
    precedencias: Dict[int, List[int]],
    prob_relajar: float = 0.4,
) -> Dict[int, List[int]]:
    """Relaja algunas precedencias para simular ramificaciones opcionales."""
    resultado: Dict[int, List[int]] = {}
    for tarea, requeridas in precedencias.items():
        if not requeridas:
            resultado[tarea] = []
            continue

        requeridas_locales: List[int] = []
        for req in requeridas:
            if random.random() > prob_relajar:
                requeridas_locales.append(req)

        if not requeridas_locales:
            requeridas_locales.append(random.choice(requeridas))

        resultado[tarea] = requeridas_locales
    return resultado


def _seleccionar_categoria(
    candidatos: List[int],
    pesos_categorias: Optional[Dict[str, float]],
) -> str:
    """Elige una categoría disponible en base a los pesos configurados."""
    categorias_disponibles = {
        TAREA_A_CATEGORIA.get(tarea) for tarea in candidatos if TAREA_A_CATEGORIA.get(tarea)
    }
    if not categorias_disponibles:
        return random.choice(list(CATEGORIAS_TAREAS.keys()))

    if not pesos_categorias:
        return random.choice(list(categorias_disponibles))

    ponderadas: List[tuple[str, float]] = []
    total = 0.0
    for categoria in categorias_disponibles:
        peso = max(pesos_categorias.get(categoria, 0.0), 0.0)
        ponderadas.append((categoria, peso))
        total += peso

    if total <= 0:
        return random.choice(list(categorias_disponibles))

    umbral = random.uniform(0, total)
    acumulado = 0.0
    for categoria, peso in ponderadas:
        acumulado += peso
        if umbral <= acumulado:
            return categoria

    return ponderadas[-1][0]


def _seleccionar_candidato(candidatos: List[int], categoria: str) -> int:
    """Selecciona una tarea aleatoria que pertenezca a la categoría solicitada."""
    filtrados = [tarea for tarea in candidatos if TAREA_A_CATEGORIA.get(tarea) == categoria]
    if not filtrados:
        return random.choice(candidatos)
    return random.choice(filtrados)
