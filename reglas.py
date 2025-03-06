import numpy as np
import random

def get_ai_allocations(num_battlefields, rule):
    print("-------------------------------")
    print("calling get_ai_allocations cuntion")
    print("-------------------------------")
    # create empty list for return value and resources variable to control how many ai has left
    allocs = []
    t_resources = 100
    c_resources = 0

    print("-------------------------------")
    print(f"will execute {rule} conditional")
    print("-------------------------------")
    # if to control that no value is repeated in final list
    if rule == "RULES 2":
        val = 0
        for b in range(num_battlefields):
            allocs.append(random.choice([i for i in range(t_resources) if i not in allocs]))
        print(f"--------------------------------------")
        print(f"first allocs config is: {allocs}")

        while_i = 0

        while sum(allocs) > 100:
            while_i = while_i + 1
            print(f"--------------------------------------")
            print(f"while executed because sum(allocs) is: {sum(allocs)}")
            print(f"interation is: {while_i}")
            for a in range(len(allocs)):
                print(f"a is: {a}")
                print(f"alloc[{a}] before extraction is: {allocs[a]}")
                if allocs[a] > 10 and (allocs[a] - 10) not in allocs:
                    allocs[a] = allocs[a] - 10
                elif allocs[a] <= 10  and allocs[a] > 0 and(allocs[a] - 1) not in allocs:
                    allocs[a] = allocs[a] - 1
                elif allocs[a] <= 0:
                    allocs[a] = random.choice([i for i in range(t_resources) if i not in allocs])

                print(f"alloc after extraction is: {allocs[a]}")

            print(f"--------------------------------------")
            print(f"new allocs config is: {allocs}")
        print(f"--------------------------------------")
        print(f"while didn't axecute because sum(allocs) is: {sum(allocs)}")
        print(f"--------------------------------------")

        return allocs

    # Make sure random number is at least 1 to avoid leaving any battlefield empty
    elif rule == "RULES 4":
        return [random.randint(1, t_resources // num_battlefields) for _ in range(num_battlefields)]
    
    # Generic ai alloc for the moment
    else:
        return  [random.randint(0, t_resources // num_battlefields) for _ in range(num_battlefields)]
    

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
"""territorios = 5
rondas = 3
asignaciones_jugador1 = [[5, 3, 2, 4, 6], [4, 2, 6, 1, 7], [3, 5, 4, 2, 6]]
asignaciones_jugador2 = [[4, 4, 3, 5, 5], [2, 3, 7, 2, 6], [5, 2, 3, 4, 7]]"""

#puntajes = calcular_puntaje(territorios, rondas, asignaciones_jugador1, asignaciones_jugador2, reglas="mayoria")
#print("Puntajes finales:", puntajes)

#prueba = get_ai_allocations(3, "RULES 2")
#print(f"Prueba: {prueba}")