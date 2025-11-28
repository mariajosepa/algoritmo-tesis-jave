import argparse
import csv
from pathlib import Path
from typing import Dict

from config.generador_instancias import generar_batch_instancias, CATEGORIAS_TAREAS
from ag.ag import run_ag
from spt.spt import run_spt
from ag.utils import exportar_csv_ag
from spt.utils import exportar_csv_spt


def ejecutar_simulaciones(
    n: int,
    output: str,
    seed: int | None = None,
    min_ot: int = 4,
    max_ot: int = 12,
    pesos_categorias: Dict[str, float] | None = None,
) -> None:
    """Genera instancias y compara AG vs SPT, consolidando resultados en un CSV."""
    instancias = generar_batch_instancias(
        n,
        min_ot=min_ot,
        max_ot=max_ot,
        seed=seed,
        pesos_categorias=pesos_categorias,
    )

    columnas = [
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

    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        output_path.unlink()

    for instancia in instancias:
        instancia_id = instancia.get("instancia_id", "instancia")
        resultado_ag = run_ag(instancia, instancia_id=instancia_id)
        resultado_spt = run_spt(instancia, instancia_id=instancia_id)
        exportar_csv_ag(resultado_ag, output)
        exportar_csv_spt(resultado_spt, output)

    print(f"Simulación completada: {len(instancias)} instancias procesadas")
    print(f"CSV guardado en: {output_path.resolve()}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Simulador comparativo AG vs SPT.")
    parser.add_argument("--n", type=int, required=True, help="Número de instancias a generar.")
    parser.add_argument("--seed", type=int, default=None, help="Semilla aleatoria opcional.")
    parser.add_argument(
        "--output",
        type=str,
        default="resultados.csv",
        help="Ruta del CSV consolidado.",
    )
    parser.add_argument("--min_ot", type=int, default=4, help="Número mínimo de OT por instancia.")
    parser.add_argument("--max_ot", type=int, default=12, help="Número máximo de OT por instancia.")
    parser.add_argument(
        "--peso_categoria",
        action="append",
        default=None,
        metavar="CATEGORIA=PESO",
        help=(
            "Ajusta el peso relativo de una categoría (BLOQUE, BIELAS, CIGUENAL, CULATA). "
            "Se puede repetir la bandera."
        ),
    )
    return parser.parse_args()


def _parse_pesos_categorias(entries: list[str] | None) -> Dict[str, float] | None:
    """Convierte entradas CLI a un dict {categoria: peso}."""
    if not entries:
        return None

    validas = {nombre.upper(): nombre for nombre in CATEGORIAS_TAREAS.keys()}
    pesos: Dict[str, float] = {}
    for entrada in entries:
        if "=" not in entrada:
            raise ValueError(f"Formato inválido para --peso_categoria: '{entrada}'")
        nombre, valor = entrada.split("=", 1)
        nombre_norm = nombre.strip().upper()
        if nombre_norm not in validas:
            raise ValueError(f"Categoría desconocida para --peso_categoria: '{nombre}'")
        try:
            peso = float(valor)
        except ValueError as err:
            raise ValueError(f"Peso inválido para '{nombre}': {valor}") from err
        pesos[validas[nombre_norm]] = peso

    return pesos


def main() -> None:
    args = parse_args()
    try:
        pesos_categorias = _parse_pesos_categorias(args.peso_categoria)
    except ValueError as exc:
        raise SystemExit(str(exc))
    ejecutar_simulaciones(
        n=args.n,
        output=args.output,
        seed=args.seed,
        min_ot=args.min_ot,
        max_ot=args.max_ot,
        pesos_categorias=pesos_categorias,
    )


if __name__ == "__main__":
    main()
