# Algoritmo Genético vs. SPT – Taller Rectificado

Este proyecto implementa y compara dos estrategias de programación de tareas para un taller: un **Algoritmo Genético (AG)** y un planificador basado en la regla **Shortest Processing Time (SPT)**. Todo el flujo está pensado para generar instancias diarias aleatorias, correr ambos algoritmos y consolidar las métricas en un único CSV.

## Estructura principal

```
proyecto/
├── ag/                  # Implementación del Algoritmo Genético
│   ├── ag.py            # run_ag, simular_individuo, fitness, etc.
│   └── utils.py         # formateo y exportación de resultados del AG
├── spt/                 # Implementación del algoritmo SPT
│   ├── spt.py           # run_spt, simular_spt, find_earliest_slot, etc.
│   └── utils.py         # formateo y exportación de resultados del SPT
├── config/
│   ├── taller_config.py # Datos estáticos del taller (tareas, precedencias, etc.)
│   └── generador_instancias.py
│                        # Generación de instancias diarias aleatorias
└── simulador.py         # Entry point para correr simulaciones masivas
```

### Archivos clave

- **proyecto/ag/ag.py**: contiene la lógica del AG (configura PyGAD, simula individuos, calcula fitness y expone `run_ag`).
- **proyecto/spt/spt.py**: implementación modular del SPT, con `run_spt`, `simular_spt`, `ordenar_spt` y `find_earliest_slot`.
- **proyecto/ag/utils.py** y **proyecto/spt/utils.py**: formatean los resultados y permiten exportarlos a CSV para comparaciones cuantitativas.
- **proyecto/config/taller_config.py**: catálogo estático del taller (tareas, duraciones base, precedencias, operarios, habilidades y horizonte estándar).
- **proyecto/config/generador_instancias.py**: genera instancias diarias aleatorias compatibles con ambos algoritmos.
- **proyecto/simulador.py**: script principal que genera instancias, ejecuta AG y SPT y escribe los resultados consolidados.
- **requirements.txt**: dependencias mínimas (numpy y pygad).
- **.gitignore**: ignora entornos virtuales, caches y archivos temporales.

## Instalación de dependencias

1. Crear y activar un entorno virtual (opcional, pero recomendado).
2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Ejecutar simulaciones

El entry point es `proyecto/simulador.py`, que acepta:

- `--n`: número de instancias a generar (obligatorio).
- `--seed`: semilla aleatoria opcional.
- `--output`: ruta del CSV consolidado (default `resultados.csv`).
- `--min_ot` / `--max_ot`: rango de órdenes de trabajo por instancia (default 4–12).
- `--peso_categoria`: pondera la probabilidad de elegir tareas por área (`BLOQUE`, `BIELAS`, `CIGUENAL`, `CULATA`). Se puede repetir para asignar varios pesos (ej. `--peso_categoria CULATA=0.6 --peso_categoria BLOQUE=0.3`).

Ejemplo:

```bash
python proyecto/simulador.py --n 20 --seed 42 --output resultados.csv \
  --peso_categoria CULATA=0.6 --peso_categoria CIGUENAL=0.1 \
  --peso_categoria BIELAS=0.1 --peso_categoria BLOQUE=0.2
```

El script:
1. Genera `n` instancias aleatorias.
2. Corre `run_ag` y `run_spt` sobre cada instancia.
3. Usa `exportar_csv_ag` y `exportar_csv_spt` para anexar los resultados al CSV.
4. Imprime un resumen indicando cuántas instancias se procesaron y la ruta del archivo generado.

Tras la ejecución tendrás un `resultados.csv` con las columnas:
`instancia_id, algoritmo, num_OT, num_tareas, tareas_ejecutadas, tareas_rechazadas, makespan, carga_total, carga_std`.

## Notas

- El simulador no muestra cronogramas ni detalles internos, sólo consolida métricas cuantitativas.
- Puedes importar `run_ag`, `run_spt` y las utilidades directamente en tus propios scripts si necesitas integraciones personalizadas.
- Ajusta `generador_instancias.py` si quieres modificar probabilidades, variabilidad de duraciones o reglas del taller.***
