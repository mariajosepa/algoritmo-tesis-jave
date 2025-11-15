"""Interfaz pública para el módulo del Algoritmo Genético."""

from .ag import (
    construir_gene_space,
    run_ag,
    run_generations,
    simular_individuo,
)

__all__ = [
    "construir_gene_space",
    "run_ag",
    "run_generations",
    "simular_individuo",
]
