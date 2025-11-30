import csv
from pathlib import Path
from statistics import pstdev
from typing import Any, Dict, Iterable, List


CSV_COLUMNS = [
    "instancia_id",
    "algoritmo",
    "num_OT",
    "num_tareas",
    "tareas_ejecutadas",
    "tareas_rechazadas",
    "makespan",
    "carga_total",
    "carga_std",
]


def formatear_resultados_ag(
    instancia: Dict[str, Any],
    instancia_id: str,
    simulacion: Dict[str, Any],
) -> Dict[str, Any]:
    """Estructura los resultados del AG en un formato uniforme."""

    tareas = instancia.get("tareas_a_programar", [])
    ots = instancia.get("ots") or sorted({ot for ot, _ in tareas})
    cronograma = simulacion.get("cronograma", [])
    tiempos_operario = simulacion.get("tiempo_por_operario", {})
    carga_por_operario = _calcular_carga_por_operario(cronograma)
    tiempos = list(carga_por_operario.values())
    carga_total = sum(tiempos)
    carga_std = pstdev(tiempos) if len(tiempos) > 1 else 0.0

    asignaciones = _generar_asignaciones(cronograma)

    resultado = {
        "algoritmo": "AG",
        "instancia_id": instancia_id,
        "num_OT": len(ots),
        "num_tareas": len(tareas),
        "tareas_ejecutadas": simulacion.get("tareas_ejecutadas", 0),
        "tareas_rechazadas": len(simulacion.get("tareas_rechazadas", [])),
        "makespan": simulacion.get("makespan", 0),
        "carga_total": carga_total,
        "carga_std": carga_std,
        "carga_por_operario": carga_por_operario,
        "tiempo_por_operario": dict(tiempos_operario),
        "intervalos_por_ot": {
            ot: sorted(intervalos)
            for ot, intervalos in simulacion.get("ocupacion_ot", {}).items()
        },
        "asignaciones": asignaciones,
    }

    return resultado


def _generar_asignaciones(cronograma: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Construye la lista de asignaciones con el orden ejecutado."""
    tareas_por_operario: Dict[Any, List[Dict[str, Any]]] = {}

    for registro in cronograma:
        operador = registro["operario"]
        tareas_por_operario.setdefault(operador, []).append(registro)

    asignaciones: List[Dict[str, Any]] = []
    for operario in sorted(tareas_por_operario):
        tareas_ordenadas = sorted(
            tareas_por_operario[operario],
            key=lambda tarea: (tarea["inicio"], tarea["fin"], tarea["idx"]),
        )
        for orden, tarea in enumerate(tareas_ordenadas, start=1):
            asignaciones.append(
                {
                    "ot": tarea["ot"],
                    "t": tarea["tarea"],
                    "operario": operario,
                    "inicio": tarea["inicio"],
                    "fin": tarea["fin"],
                    "orden": orden,
                }
            )

    return asignaciones


def _calcular_carga_por_operario(
    cronograma: Iterable[Dict[str, Any]]
) -> Dict[Any, int]:
    """Acumula el tiempo real trabajado por cada operario."""
    carga: Dict[Any, int] = {}
    for registro in cronograma:
        operario = registro["operario"]
        duracion = int(registro["fin"]) - int(registro["inicio"])
        carga[operario] = carga.get(operario, 0) + max(0, duracion)
    return carga


def exportar_csv_ag(resultado: Dict[str, Any], ruta: str) -> None:
    """Agrega el resultado a un CSV orientado a métricas comparativas."""

    csv_path = Path(ruta)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    escribir_encabezado = not csv_path.exists()

    with csv_path.open("a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=CSV_COLUMNS)
        if escribir_encabezado:
            writer.writeheader()
        writer.writerow({columna: resultado.get(columna) for columna in CSV_COLUMNS})
