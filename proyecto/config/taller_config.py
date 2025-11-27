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
  # BLOQUE (1–14) — SOLO operarios 1-4 (Bloqueros)
  # ============================================================

  1:  [1, 2],        # inspección 
  2:  [3],           # prueba hidrostatica 
  3:  [2, 4],        # extraer camisas
  4:  [3, 4],        # encamisar bloque (difícil)
  5:  [2, 4],        # rectificar cilindros
  6:  [3, 4],        # glasear bloque 
  7:  [4],           # cepillar superficie 
  8:  [2, 4],        # reconstruir bancada 
  9:  [1],           # asentar bancada 
  10: [3, 4],        # alinear bancada 
  11: [1, 3],        # limpiar galerías
  12: [2, 4],        # ensamblar bloque
  13: [3, 4],        # prueba presión
  14: [1, 4],        # pintar bloque

  # ============================================================
  # BIELAS (15–19) — SOLO operarios 1–18
  # ============================================================

  15: [7, 8],            # asentar bielas 
  16: [8, 9, 10],        # instalar bielas 
  17: [9, 10],           # refrentar pistón 
  18: [10, 11, 12],      # instalar pistón 
  19: [11, 12, 13, 14],  # armar conjunto

  # ============================================================
  # CIGÜEÑAL (20–24) — SOLO operarios 1–2
  # ============================================================

  20: [1],        # metalizar moñón 
  21: [1, 2],     # pulir cigüeñal 
  22: [2],        # rectificar moñón biela 
  23: [1, 2],     # rectificar moñón bancada 
  24: [1, 2],     # balancear cigüeñal

  # ============================================================
  # CULATAS (25–35) SOLO operarios 7-18
  # ============================================================

  25: [7, 8],              # prueba hidrostatica culata
  26: [8, 9, 10],          # instalar guías
  27: [9, 10],             # adaptar guías
  28: [10, 11, 12],        # fabricar guías
  29: [11, 12],            # rimar guías
  30: [12, 13, 14],        # espiralar guías
  31: [13],                # instalar camisillas
  32: [13, 14, 15],        # reconstruir alojamiento
  33: [14, 15],            # rectificar base camisilla
  34: [15, 16, 17, 18],    # cepillar culata
  35: [10, 12, 14, 16, 18] # rectificar válvulas
}
 
# ============================================================
#  HORIZONTE
# ============================================================
 
HORIZONTE = 480
 