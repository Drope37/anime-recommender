import csv
import os
import random

def leer_animes(nombre_archivo):
    animes = []
    
    with open(nombre_archivo, newline="", encoding="utf-8") as archivo:
        lector = csv.reader(archivo)
        
        for fila in lector:
            nombre, coeficiente_texto = fila
            animes.append((nombre, float(coeficiente_texto)))
    
    return animes
            
def elegir_anime(animes):
    nombres = []
    coeficientes = []
    
    for nombre, coeficiente in animes:
        nombres.append(nombre)
        coeficientes.append(coeficiente)
    
    return random.choices(nombres, weights=coeficientes)[0]

def main():
    ruta_base = os.path.dirname(__file__)
    nombre_archivo = os.path.join(ruta_base, 'animes_output.csv')

    animes = leer_animes(nombre_archivo)
    resultado = elegir_anime(animes)
    
    print(resultado)

if __name__ == "__main__":
    main()
