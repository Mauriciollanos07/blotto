import numpy as np

def calcular_puntaje(territorios, rondas, asignaciones_jugador1, asignaciones_jugador2, reglas="mayoria"):
    """
    Calcula el puntaje de un juego de Blotto.

    :param territorios: Número de territorios a disputar.
    :param rondas: Número de rondas a jugar.
    :param asignaciones_jugador1: Lista de listas con las asignaciones de tropas del Jugador 1 para cada ronda.
    :param asignaciones_jugador2: Lista de listas con las asignaciones de tropas del Jugador 2 para cada ronda.
    :param reglas: Tipo de reglas a aplicar ("mayoria", "proporcion", etc.).
    :return: Tupla con los puntajes finales de (Jugador 1, Jugador 2).
    """
    
    puntaje_j1 = 0
    puntaje_j2 = 0
    
    for ronda in range(rondas):
        tropas_j1 = asignaciones_jugador1[ronda]
        tropas_j2 = asignaciones_jugador2[ronda]

        for t in range(territorios):
            if reglas == "mayoria":
                # El jugador con más tropas gana el punto
                if tropas_j1[t] > tropas_j2[t]:
                    puntaje_j1 += 1
                elif tropas_j2[t] > tropas_j1[t]:
                    puntaje_j2 += 1
                # En caso de empate, no se otorgan puntos
            
            elif reglas == "proporcion":
                # Se asignan puntos proporcionales a la inversión de tropas
                total_tropas = tropas_j1[t] + tropas_j2[t]
                if total_tropas > 0:
                    puntaje_j1 += (tropas_j1[t] / total_tropas)
                    puntaje_j2 += (tropas_j2[t] / total_tropas)

    return round(puntaje_j1, 2), round(puntaje_j2, 2)

# Ejemplo de uso
territorios = 5
rondas = 3
asignaciones_jugador1 = [[5, 3, 2, 4, 6], [4, 2, 6, 1, 7], [3, 5, 4, 2, 6]]
asignaciones_jugador2 = [[4, 4, 3, 5, 5], [2, 3, 7, 2, 6], [5, 2, 3, 4, 7]]

puntajes = calcular_puntaje(territorios, rondas, asignaciones_jugador1, asignaciones_jugador2, reglas="mayoria")
print("Puntajes finales:", puntajes)