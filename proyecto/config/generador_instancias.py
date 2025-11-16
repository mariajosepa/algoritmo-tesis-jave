from typing import Dict, Any, List
import random
from .taller_config import (
    TAREAS,
    PRECEDENCIAS,
    DURACIONES_BASE,
    OPERARIOS,
    OPERARIOS_APTOS,
    HORIZONTE,
)


def generar_instancia(
    instancia_id: str,
    num_ot: int,
    min_tareas_por_ot: int = 3,
    max_tareas_por_ot: int = 7,
    variabilidad_duracion: float = 0.10,
    prob_falta_repuesto: float = 0.15
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
    seed: int | None = None
) -> List[Dict[str, Any]]:
    """Genera un conjunto de instancias aleatorias."""
    if seed is not None:
        random.seed(seed)

    batch = []
    for i in range(n):
        num_ot = random.randint(min_ot, max_ot)
        batch.append(generar_instancia(f"inst_{i}", num_ot))
    return batch


def _seleccionar_tareas_validas(
    cantidad: int,
    universo: List[int],
    precedencias: Dict[int, List[int]],
) -> List[int]:
    """Selecciona un subconjunto de tareas que respeta todas las precedencias."""
    seleccionadas: List[int] = []
    candidatos = universo.copy()
    random.shuffle(candidatos)

    for tarea in candidatos:
        if len(seleccionadas) >= cantidad:
            break
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
