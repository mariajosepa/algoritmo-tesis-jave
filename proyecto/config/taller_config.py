# ============================================================
#  TAREAS REALES DEL TALLER DE RECTIFICADO (35 tareas)
# ============================================================
 
TAREAS = {
   # --- BLOQUE (1–14) ---
   "INSPECCION_BLOQUE": 1,
   "PRUEBA_HIDROSTATICA_BLOQUE": 2,
   "EXTRAER_CAMISAS": 3,
   "ENCAMISAR_BLOQUE": 4,
   "RECTIFICAR_CILINDROS": 5,
   "GLASEAR_BLOQUE": 6,
   "CEPILLAR_SUPERFICIE": 7,
   "RECONSTRUIR_BANCADA": 8,
   "ASENTAR_BANCADA": 9,
   "ALINEAR_BANCADA": 10,
   "LIMPIAR_GALERIAS": 11,
   "ENSAMBLAR_BLOQUE": 12,
   "PRUEBA_PRESION_BLOQUE": 13,
   "PINTAR_BLOQUE": 14,
 
   # --- BIELAS (15–19) ---
   "ASENTAR_BIELAS": 15,
   "INSTALAR_BIELAS": 16,
   "REFRENTAR_PISTON": 17,
   "INSTALAR_PISTON": 18,
   "ARMAR_CONJUNTO_BIELA_PISTON": 19,
 
   # --- CIGUEÑAL (20–24) ---
   "METALIZAR_MOÑON_CIGUENAL": 20,
   "PULIR_CIGUENAL": 21,
   "RECTIFICAR_MOÑON_BIELA": 22,
   "RECTIFICAR_MOÑON_BANCADA": 23,
   "BALANCEAR_CIGUENAL": 24,
 
   # --- CULATAS (25–35) ---
   "PRUEBA_HIDROSTATICA_CULATA": 25,
   "INSTALAR_GUIAS": 26,
   "ADAPTAR_GUIAS": 27,
   "FABRICAR_GUIAS": 28,
   "RIMAR_GUIAS": 29,
   "ESPIRALAR_GUIAS": 30,
   "INSTALAR_CAMISILLAS": 31,
   "RECONSTRUIR_ALOJAMIENTO_CAMISILLA": 32,
   "RECTIFICAR_BASE_CAMISILLA": 33,
   "CEPILLAR_CULATA": 34,
   "RECTIFICAR_VALVULAS": 35,
}
 
TAREAS_INV = {idx: nombre for nombre, idx in TAREAS.items()}
 

# ============================================================
#  PRECEDENCIAS REALISTAS (COMPLEJAS Y LÓGICAS)
# ============================================================
 
PRECEDENCIAS = {
   # -------- BLOQUE --------
   1:  [],
   2:  [1],
   3:  [2],
   4:  [3],
   5:  [4],
   6:  [5],
   7:  [5, 6],
   8:  [7],
   9:  [7, 8],
   10: [8, 9],
   11: [6, 7],
   12: [10, 11],
   13: [12],
   14: [12, 13],
 
   # -------- BIELAS --------
   15: [],
   16: [15],
   17: [15],
   18: [16, 17],
   19: [18],
 
   # -------- CIGUEÑAL --------
   20: [],
   21: [20],
   22: [20],
   23: [20],
   24: [21, 22, 23],
 
   # -------- CULATAS --------
   25: [],
   26: [25],
   27: [26],
   28: [26],
   29: [27, 28],
   30: [29],
   31: [26, 29],
   32: [31],
   33: [31, 32],
   34: [33],
   35: [30, 33, 34],
}
 

# ============================================================
#  DURACIONES REALISTAS (BLOQUE > CULATA)
# ============================================================
 
DURACIONES_BASE = {
   # BLOQUE
   1: 15,
   2: 20,
   3: 25,
   4: 30,
   5: 45,
   6: 35,
   7: 30,
   8: 50,
   9: 40,
   10: 45,
   11: 20,
   12: 55,
   13: 25,
   14: 18,
 
   # BIELAS
   15: 20,
   16: 25,
   17: 18,
   18: 25,
   19: 30,
 
   # CIGÜEÑAL
   20: 35,
   21: 25,
   22: 40,
   23: 40,
   24: 30,
 
   # CULATAS
   25: 20,
   26: 25,
   27: 18,
   28: 22,
   29: 25,
   30: 20,
   31: 28,
   32: 35,
   33: 28,
   34: 35,
   35: 30,
}
 

# ============================================================
#  OPERARIOS DEL TALLER (6 BLOQUE, 12 CULATAS)
# ============================================================
 
BLOQUES = [1, 2, 3, 4, 5, 6]
CULATAS = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
 
OPERARIOS = BLOQUES + CULATAS
 
OPERARIOS_APTOS = {

    # ============================================================
    # OPERARIOS DE BLOQUE (1–6)
    # ============================================================

    1:  [1, 9, 11, 14, 20, 23, 35],          
    2:  [1, 3, 5, 8, 10, 12, 20, 22, 25, 26, 29],
    3:  [1, 4, 6, 7, 10, 11, 13],
    4:  [2, 3, 4, 5, 7, 8, 10, 12, 13, 14],
    5:  [3, 5, 6, 10, 14, 19, 22, 28, 30],
    6:  [4, 6, 7, 8, 10, 12, 13, 19, 21, 24],

    # ============================================================
    # OPERARIOS DE CULATAS (7–18)
    # ============================================================

    7:  [15, 25],
    8:  [15, 16, 26],
    9:  [16, 17, 27],
    10: [17, 18, 21, 28, 35],
    11: [18, 19, 22, 29, 31],
    12: [19, 20, 23, 28, 30, 32, 35],
    13: [19, 21, 23, 30, 31, 32, 33],
    14: [20, 22, 23, 30, 31, 33, 34],
    15: [23, 24, 32, 33, 34, 35],
    16: [24, 28, 30, 32, 33, 34, 35],
    17: [24, 29, 33, 34, 35],
    18: [24, 30, 31, 34, 35],
}

# ============================================================
#  HORIZONTE
# ============================================================
 
HORIZONTE = 480
 