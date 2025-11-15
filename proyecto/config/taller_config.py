TAREAS = {
    "INSPECCION_INICIAL": 1,
    "DESMONTAJE": 2,
    "LAVADO": 3,
    "ARENADO": 4,
    "REEMPLAZO_COMPONENTES": 5,
    "ENSAMBLAJE": 6,
    "ALINEACION": 7,
    "PRUEBAS_FUNCIONALES": 8,
    "PINTURA_FINAL": 9,
    "ENTREGA": 10,
}

TAREAS_INV = {idx: nombre for nombre, idx in TAREAS.items()}

PRECEDENCIAS = {
    1: [],
    2: [1],
    3: [2],
    4: [2, 3],
    5: [2],
    6: [4, 5],
    7: [6],
    8: [6, 7],
    9: [4],
    10: [8, 9],
}

DURACIONES_BASE = {
    1: 15,
    2: 25,
    3: 20,
    4: 30,
    5: 35,
    6: 28,
    7: 18,
    8: 22,
    9: 26,
    10: 12,
}

OPERARIOS = [1, 2, 3, 4, 5, 6, 7, 8]

OPERARIOS_APTOS = {
    1: [1, 2, 3],
    2: [2, 3, 4, 5],
    3: [3, 4, 6],
    4: [4, 5, 6, 7],
    5: [5, 6, 8],
    6: [6, 7, 8, 9],
    7: [7, 8, 9],
    8: [8, 9, 10],
}

HORIZONTE = 120
