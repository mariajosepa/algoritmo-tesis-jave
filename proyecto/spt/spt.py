from __future__ import annotations

from typing import Any, Dict, Iterable, List, Sequence, Set, Tuple

from .utils import formatear_resultados_spt


def run_spt(instancia: Dict[str, Any], instancia_id: str = "instancia") -> Dict[str, Any]:
    """Ejecuta el algoritmo SPT y retorna los resultados formateados."""
    simulacion = simular_spt(instancia)
    return formatear_resultados_spt(instancia, instancia_id, simulacion)


def simular_spt(instancia: Dict[str, Any]) -> Dict[str, Any]:
    """Aplica la regla SPT sobre la instancia respetando todas las restricciones."""
    tareas_plan = instancia.get("tareas_a_programar") or instancia.get("Tareas_a_Programar")
    if not tareas_plan:
        raise ValueError("La instancia debe contener 'tareas_a_programar'.")
    tareas: List[Tuple[int, int]] = [tuple(tarea) for tarea in tareas_plan]

    tiempos_procesamiento = (
        instancia.get("tiempos_procesamiento") or instancia.get("tiempos") or {}
    )
    prerequisitos = instancia.get("prerequisitos", {})
    repuestos_por_ot = instancia.get("repuestos_por_ot") or instancia.get("prerequisitos_Repuestos") or {}
    operarios = instancia.get("operarios") or instancia.get("O")
    if not operarios:
        raise ValueError("La instancia debe contener la lista de operarios disponibles.")
    operarios = [int(op) for op in operarios]
    operarios_aptos_raw = instancia.get("operarios_aptos") or instancia.get("Operarios_aptos") or {}
    operarios_aptos = {
        int(op): [int(tarea) for tarea in tareas_op]
        for op, tareas_op in operarios_aptos_raw.items()
    }
    ots = instancia.get("ots") or instancia.get("OT") or sorted({ot for ot, _ in tareas})
    mapeo_ot = instancia.get("mapeo_ot") or instancia.get("mapeo") or {}
    horizonte = instancia.get("horizonte") or instancia.get("H")
    if horizonte is None:
        raise ValueError("La instancia debe definir un horizonte ('horizonte' o 'H').")

    pendientes: Set[Tuple[int, int]] = set(tareas)
    completadas_por_ot: Dict[int, Set[int]] = {ot: set() for ot in ots}
    ocupacion_ot: Dict[int, List[Tuple[int, int]]] = {ot: [] for ot in ots}
    tiempo_por_operario: Dict[int, int] = {int(op): 0 for op in operarios}
    orden_operario: Dict[int, int] = {int(op): 0 for op in operarios}
    cronograma: List[Dict[str, Any]] = []
    tareas_rechazadas: List[Dict[str, Any]] = []
    indice_tarea = {tuple_tarea: idx for idx, tuple_tarea in enumerate(tareas)}

    contexto_orden = {
        "pendientes": pendientes,
        "completadas_por_ot": completadas_por_ot,
        "mapeo_ot": mapeo_ot,
        "prerequisitos": prerequisitos,
        "repuestos_por_ot": repuestos_por_ot,
        "tiempos_procesamiento": tiempos_procesamiento,
    }

    progreso = True
    while pendientes and progreso:
        progreso = False
        tareas_listas = ordenar_spt(contexto_orden)
        if not tareas_listas:
            break

        for (ot, tarea) in tareas_listas:
            if (ot, tarea) not in pendientes:
                continue

            candidatos = [op for op in operarios if tarea in operarios_aptos.get(op, [])]
            if not candidatos:
                continue

            duracion = tiempos_procesamiento.get(tarea)
            if duracion is None:
                raise ValueError(f"No se definió duración para la tarea {tarea}.")

            asignado = False
            for operario in sorted(candidatos, key=lambda op: tiempo_por_operario[int(op)]):
                op_int = int(operario)
                earliest = tiempo_por_operario[op_int]
                ok, inicio, fin = find_earliest_slot(ocupacion_ot[ot], earliest, int(duracion), int(horizonte))
                if ok:
                    tiempo_por_operario[op_int] = fin
                    ocupacion_ot[ot].append((inicio, fin))
                    completadas_por_ot.setdefault(ot, set()).add(tarea)
                    orden_operario[op_int] += 1
                    pendientes.remove((ot, tarea))
                    cronograma.append(
                        {
                            "idx": indice_tarea[(ot, tarea)],
                            "ot": ot,
                            "tarea": tarea,
                            "operario": op_int,
                            "inicio": inicio,
                            "fin": fin,
                            "orden": orden_operario[op_int],
                        }
                    )
                    progreso = True
                    asignado = True
                    break

            if not asignado:
                continue

    cronograma.sort(key=lambda tarea: (tarea["operario"], tarea["inicio"], tarea["fin"]))
    tareas_rechazadas = [{"ot": ot, "tarea": tarea} for ot, tarea in sorted(pendientes)]
    makespan = max(tiempo_por_operario.values()) if tiempo_por_operario else 0

    return {
        "cronograma": cronograma,
        "tareas_rechazadas": tareas_rechazadas,
        "tiempo_por_operario": tiempo_por_operario,
        "ocupacion_ot": {ot: sorted(intervalos) for ot, intervalos in ocupacion_ot.items()},
        "tareas_ejecutadas": len(cronograma),
        "makespan": makespan,
        "n_tareas": len(tareas),
    }


def ordenar_spt(instancia: Dict[str, Any]) -> List[Tuple[int, int]]:
    """Filtra las tareas listas y las ordena por regla SPT."""
    pendientes: Set[Tuple[int, int]] = instancia.get("pendientes", set())
    mapeo_ot = instancia.get("mapeo_ot", {})
    prerequisitos = instancia.get("prerequisitos", {})
    repuestos = instancia.get("repuestos_por_ot", {})
    completadas = instancia.get("completadas_por_ot", {})
    tiempos_procesamiento = instancia.get("tiempos_procesamiento", {})

    tareas_listas: List[Tuple[int, int]] = []
    for (ot, tarea) in pendientes:
        if not _prerequisitos_locales_cumplidos(ot, tarea, mapeo_ot, prerequisitos, completadas):
            continue
        if not _repuesto_disponible(ot, tarea, mapeo_ot, repuestos):
            continue
        duracion = tiempos_procesamiento.get(tarea)
        if duracion is None:
            raise ValueError(f"No se definió duración para la tarea {tarea}.")
        tareas_listas.append((ot, tarea))

    tareas_listas.sort(key=lambda item: (int(tiempos_procesamiento[item[1]]), item[0], item[1]))
    return tareas_listas


def find_earliest_slot(
    occ_list: Sequence[Tuple[int, int]],
    earliest_start: int,
    duration: int,
    horizonte: int,
) -> Tuple[bool, int, int]:
    """
    Busca el primer hueco [s,f) >= earliest_start en occ_list donde quepa 'duration'.
    """
    s = max(0, earliest_start)
    if not occ_list:
        f = s + duration
        return (f <= horizonte, s, f)

    intervals = sorted(occ_list, key=lambda intervalo: intervalo[0])

    first_s, first_f = intervals[0]
    f = s + duration
    if f <= first_s and f <= horizonte:
        return True, s, f

    for i in range(len(intervals) - 1):
        s_i, f_i = intervals[i]
        s_next, _ = intervals[i + 1]
        s = max(s, f_i)
        f = s + duration
        if f <= s_next and f <= horizonte:
            return True, s, f

    s_last, f_last = intervals[-1]
    s = max(s, f_last)
    f = s + duration
    if f <= horizonte:
        return True, s, f

    return False, -1, -1


def _prerequisitos_locales_cumplidos(
    ot: int,
    tarea: int,
    mapeo_ot: Dict[int, List[int]],
    prerequisitos: Dict[int, Iterable[int]],
    completadas_por_ot: Dict[int, Set[int]],
) -> bool:
    tipos_en_ot = set(mapeo_ot.get(ot, []))
    prereqs_totales = set(prerequisitos.get(tarea, []))
    prereqs_exigibles = prereqs_totales.intersection(tipos_en_ot)
    completadas = completadas_por_ot.get(ot, set())
    return prereqs_exigibles.issubset(completadas)


def _repuesto_disponible(
    ot: int,
    tarea: int,
    mapeo_ot: Dict[int, List[int]],
    repuestos_por_ot: Dict[int, List[int]],
) -> bool:
    if ot not in mapeo_ot:
        return False
    tareas_ot = mapeo_ot[ot]
    if tarea not in tareas_ot:
        return False
    idx = tareas_ot.index(tarea)
    repuestos = repuestos_por_ot.get(ot, [])
    return idx < len(repuestos) and bool(repuestos[idx])
