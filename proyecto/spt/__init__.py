"""Interfaz pública para el módulo del algoritmo SPT."""

from .spt import find_earliest_slot, ordenar_spt, run_spt, simular_spt

__all__ = [
    "run_spt",
    "simular_spt",
    "ordenar_spt",
    "find_earliest_slot",
]
