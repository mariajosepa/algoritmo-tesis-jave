from __future__ import annotations

from collections import defaultdict
from functools import partial
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import pygad

from .utils import formatear_resultados_ag


DEFAULT_GA_CONFIG: Dict[str, Any] = {
    "num_generations": 200,
    "num_parents_mating": 10,
    "sol_per_pop": 100,
    "parent_selection_type": "rank",
    "keep_parents": 5,
    "crossover_type": "single_point",
    "mutation_type": "random",
    "mutation_percent_genes": 25,
    "random_seed": 42,
}


def run_ag(instancia: Dict[str, Any], instancia_id: str = "instancia") -> Dict[str, Any]:
    """Ejecuta el AG, formatea los resultados y los retorna listos para consumir."""
    resultado_ga = run_generations(instancia)
    simulacion = resultado_ga["simulacion"]
    return formatear_resultados_ag(instancia, instancia_id, simulacion)


def construir_gene_space(instancia: Dict[str, Any]) -> List[Any]:
    """Crea el gene_space combinando asignación de operarios y prioridades."""
    tareas = instancia.get("tareas_a_programar", [])
    n_tareas = len(tareas)
    operarios_por_tarea = _operarios_por_tarea(instancia)

    gene_space: List[Any] = []
    for _, tarea in tareas:
        opciones = operarios_por_tarea.get(tarea, [])
        if not opciones:
            raise ValueError(f"No hay operarios aptos para la tarea {tarea}")
        gene_space.append(sorted(opciones))

    gene_space.extend({"low": 0.0, "high": 1.0} for _ in range(n_tareas))
    return gene_space


def fitness_func(
    solution: Sequence[float],
    solution_idx: int,
    instancia: Optional[Dict[str, Any]] = None,
) -> float:
    """Evalúa un individuo calculando su fitness a partir de la simulación."""
    if instancia is None:
        raise ValueError("Se requiere la instancia del problema para evaluar el fitness.")

    simulacion = simular_individuo(solution, instancia)
    penalizaciones = simulacion["penalizaciones"]

    fitness = (
        100 * simulacion["tareas_ejecutadas"]
        - 10 * penalizaciones["prerequisitos"]
        - 10 * penalizaciones["repuestos"]
        - 15 * penalizaciones["operario_no_apto"]
        - 12 * penalizaciones["ot_ocupada"]
        - 0.1 * penalizaciones["exceso_tiempo"]
        - 0.5 * simulacion["desbalance"]
        - 0.1 * simulacion["makespan"]
    )
    return float(fitness)


def simular_individuo(
    genotipo: Sequence[float],
    instancia: Dict[str, Any],
) -> Dict[str, Any]:
    """Simula la ejecución del cromosoma y devuelve métricas detalladas."""
    tareas = instancia.get("tareas_a_programar", [])
    if not tareas:
        raise ValueError("La instancia no contiene tareas a programar.")

    n_tareas = len(tareas)
    if len(genotipo) < 2 * n_tareas:
        raise ValueError("El genotipo recibido no tiene la longitud esperada.")

    tiempos_procesamiento = instancia.get("tiempos_procesamiento", {})
    horizonte = instancia.get("horizonte")
    if horizonte is None:
        raise ValueError("La instancia debe definir un horizonte de planificación.")
    operarios = instancia.get("operarios") or sorted(
        instancia.get("operarios_aptos", {}).keys()
    )
    operarios_por_tarea = _operarios_por_tarea(instancia)
    repuestos_por_ot = instancia.get("repuestos_por_ot", {})
    mapeo_ot = instancia.get("mapeo_ot", {})
    prerequisitos = instancia.get("prerequisitos", {})

    genes = np.asarray(genotipo)
    operarios_asignados = genes[:n_tareas].astype(int)
    prioridades = genes[n_tareas:]

    tareas_por_operario: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
    for idx, (ot, tarea) in enumerate(tareas):
        duracion = tiempos_procesamiento.get(tarea)
        if duracion is None:
            raise ValueError(f"No se definió duración para la tarea {tarea}.")

        operario = int(operarios_asignados[idx])
        tareas_por_operario[operario].append(
            {
                "idx": idx,
                "ot": ot,
                "tarea": tarea,
                "prioridad": float(prioridades[idx]),
                "duracion": int(duracion),
            }
        )

    for registros in tareas_por_operario.values():
        registros.sort(key=lambda item: item["prioridad"], reverse=True)

    tiempo_por_operario = {int(op): 0 for op in operarios}
    tareas_completadas_por_ot: Dict[int, set] = defaultdict(set)
    ocupacion_ot: Dict[int, List[Tuple[int, int]]] = defaultdict(list)
    cronograma: List[Dict[str, Any]] = []
    tareas_rechazadas: List[Dict[str, Any]] = []
    penalizaciones = {
        "prerequisitos": 0,
        "repuestos": 0,
        "operario_no_apto": 0,
        "exceso_tiempo": 0,
        "ot_ocupada": 0,
    }

    for operario, tareas_operario in tareas_por_operario.items():
        tiempo_por_operario.setdefault(operario, 0)
        for tarea_info in tareas_operario:
            idx = tarea_info["idx"]
            ot = tarea_info["ot"]
            tarea = tarea_info["tarea"]
            duracion = tarea_info["duracion"]

            if not _operario_es_apto(tarea, operario, operarios_por_tarea):
                penalizaciones["operario_no_apto"] += 1
                tareas_rechazadas.append(
                    {"ot": ot, "tarea": tarea, "operario": operario, "motivo": "operario"}
                )
                continue

            if not _tiene_repuesto(ot, tarea, mapeo_ot, repuestos_por_ot):
                penalizaciones["repuestos"] += 1
                tareas_rechazadas.append(
                    {"ot": ot, "tarea": tarea, "operario": operario, "motivo": "repuesto"}
                )
                continue

            if not _prerequisitos_cumplidos(
                tarea, ot, prerequisitos, mapeo_ot, tareas_completadas_por_ot
            ):
                penalizaciones["prerequisitos"] += 1
                tareas_rechazadas.append(
                    {"ot": ot, "tarea": tarea, "operario": operario, "motivo": "prerequisito"}
                )
                continue

            inicio = tiempo_por_operario[operario]
            fin = inicio + duracion

            if fin > horizonte:
                penalizaciones["exceso_tiempo"] += fin - horizonte
                tareas_rechazadas.append(
                    {"ot": ot, "tarea": tarea, "operario": operario, "motivo": "horizonte"}
                )
                continue

            if not _ot_disponible(ot, inicio, fin, ocupacion_ot):
                penalizaciones["ot_ocupada"] += 1
                tareas_rechazadas.append(
                    {"ot": ot, "tarea": tarea, "operario": operario, "motivo": "ot_ocupada"}
                )
                continue

            cronograma.append(
                {
                    "idx": idx,
                    "ot": ot,
                    "tarea": tarea,
                    "operario": operario,
                    "inicio": inicio,
                    "fin": fin,
                }
            )
            tareas_completadas_por_ot[ot].add(tarea)
            ocupacion_ot[ot].append((inicio, fin))
            tiempo_por_operario[operario] = fin

    tiempos = list(tiempo_por_operario.values())
    makespan = max(tiempos) if tiempos else 0
    desbalance = float(np.std(tiempos)) if tiempos else 0.0

    return {
        "cronograma": cronograma,
        "tareas_rechazadas": tareas_rechazadas,
        "tiempo_por_operario": tiempo_por_operario,
        "ocupacion_ot": dict(ocupacion_ot),
        "tareas_ejecutadas": len(cronograma),
        "penalizaciones": penalizaciones,
        "makespan": makespan,
        "desbalance": desbalance,
        "n_tareas": n_tareas,
    }


def run_generations(instancia: Dict[str, Any]) -> Dict[str, Any]:
    """Crea la instancia del GA, la ejecuta y devuelve los datos clave."""
    tareas = instancia.get("tareas_a_programar", [])
    if not tareas:
        raise ValueError("Debe proporcionar al menos una tarea a programar.")

    n_tareas = len(tareas)
    gene_space = construir_gene_space(instancia)
    ga_params = {**DEFAULT_GA_CONFIG, **instancia.get("ga_config", {})}

    def fitness_wrapper(ga_instance, solution, solution_idx):
        return fitness_func(solution, solution_idx, instancia)

    ga_params.update(
        {
            "fitness_func": fitness_wrapper,
            "num_genes": len(gene_space),
            "gene_space": gene_space,
        }
    )

    ga_instance = pygad.GA(**ga_params)
    ga_instance.run()

    solution, fitness, solution_idx = ga_instance.best_solution()
    simulacion = simular_individuo(solution, instancia)
    simulacion.update(
        {
            "fitness": float(fitness),
            "generaciones": ga_instance.generations_completed,
            "best_solutions_fitness": getattr(ga_instance, "best_solutions_fitness", []),
        }
    )

    return {
        "solution": solution,
        "fitness": float(fitness),
        "solution_idx": solution_idx,
        "simulacion": simulacion,
    }


def _operarios_por_tarea(instancia: Dict[str, Any]) -> Dict[int, List[int]]:
    """Genera el mapeo tarea -> operarios aptos."""
    if "operarios_por_tarea" in instancia:
        return {
            tarea: sorted(operarios)
            for tarea, operarios in instancia["operarios_por_tarea"].items()
        }

    operarios_aptos = instancia.get("operarios_aptos", {})
    resultado: Dict[int, List[int]] = defaultdict(list)
    for operario, tareas in operarios_aptos.items():
        for tarea in tareas:
            resultado[tarea].append(int(operario))
    return {tarea: sorted(ops) for tarea, ops in resultado.items()}


def _operario_es_apto(
    tarea: int, operario: int, operarios_por_tarea: Dict[int, List[int]]
) -> bool:
    return operario in operarios_por_tarea.get(tarea, [])


def _tiene_repuesto(
    ot: int,
    tarea: int,
    mapeo_ot: Dict[int, List[int]],
    repuestos_por_ot: Dict[int, List[int]],
) -> bool:
    tareas_ot = mapeo_ot.get(ot, [])
    if tarea not in tareas_ot:
        return False
    idx = tareas_ot.index(tarea)
    repuestos = repuestos_por_ot.get(ot, [])
    return idx < len(repuestos) and bool(repuestos[idx])


def _prerequisitos_cumplidos(
    tarea: int,
    ot: int,
    prerequisitos: Dict[int, Iterable[int]],
    mapeo_ot: Dict[int, List[int]],
    tareas_completadas_por_ot: Dict[int, set],
) -> bool:
    prereqs = prerequisitos.get(tarea, [])
    tareas_en_ot = mapeo_ot.get(ot, [])
    completadas = tareas_completadas_por_ot.get(ot, set())
    relevantes = [p for p in prereqs if p in tareas_en_ot]
    return all(req in completadas for req in relevantes)


def _ot_disponible(
    ot: int,
    inicio: int,
    fin: int,
    ocupacion_ot: Dict[int, List[Tuple[int, int]]],
) -> bool:
    for inicio_ocupado, fin_ocupado in ocupacion_ot.get(ot, []):
        if inicio < fin_ocupado and fin > inicio_ocupado:
            return False
    return True
