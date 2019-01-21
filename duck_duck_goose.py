import random
lista = ['juan', 'pepe', 'marcos', 'luis']

def juego(lista):
    jugador = random.choice(lista)
    print('La oca es: ', lista[1])
juego(lista)
