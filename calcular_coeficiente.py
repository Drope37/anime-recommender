import csv
import math
import os
import requests

ANILIST_URL = 'https://graphql.anilist.co'
ESTANDAR_MINUTOS = 288  # 12 episodios x 24 minutos
PORCENTAJE_VALORACION = 0.7

def fetch_anilist_data(anime_id):
    query = '''
    query ($idAnime: Int) {
        Media(id: $idAnime) {
            title { romaji }
            episodes
            duration
            averageScore
        }
    }
    '''
    variables = {"idAnime": anime_id}
    
    respuesta = requests.post(ANILIST_URL, json={"query": query, "variables": variables})
    datos = respuesta.json()

    nombre = datos["data"]["Media"]["title"]["romaji"]
    score = datos["data"]["Media"]["averageScore"]
    duracion = datos["data"]["Media"]["duration"]
    episodios = datos["data"]["Media"]["episodes"]
    
    return nombre, score, duracion, episodios

def calcular_coeficiente(score, duracion, episodios):
    if episodios is None:
        return
    else:
        minutos_totales = duracion * episodios
        coeficiente_duracion = 1 / (1 + 0.625 * math.log(minutos_totales / ESTANDAR_MINUTOS))
        coeficiente_final = (score / 100) * PORCENTAJE_VALORACION + coeficiente_duracion * (1 - PORCENTAJE_VALORACION)
        
        return coeficiente_final

def procesar_lista(ruta_entrada, ruta_salida):
    with open (ruta_entrada, newline="", encoding="utf-8") as archivo_entrada, \
        open (ruta_salida, 'w', newline="", encoding="utf-8") as archivo_salida:
            
        reader = csv.reader(archivo_entrada)
        writer = csv.writer(archivo_salida)
        
        for fila in reader:
            id = int(fila[0])
            nombre, score, duracion, episodios = fetch_anilist_data(id)
            coeficiente = calcular_coeficiente(score, duracion, episodios)
            
            if coeficiente is not None:
                writer.writerow([nombre, coeficiente])
   
if __name__ == "__main__":
    ruta_base = os.path.dirname(__file__)
    ruta_entrada = os.path.join(ruta_base, 'animes_ids.csv')
    ruta_salida = os.path.join(ruta_base, 'animes_output.csv')
    
    procesar_lista(ruta_entrada, ruta_salida)
