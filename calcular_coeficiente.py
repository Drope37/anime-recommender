import csv
import math
import os
import requests
import time

ANILIST_URL = 'https://graphql.anilist.co'
ESTANDAR_MINUTOS = 288  # 12 episodios x 24 minutos
PORCENTAJE_SCORE = 0.7

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
    
    try:
        response = requests.post(ANILIST_URL, json={"query": query, "variables": variables})
        if response.status_code == 429:
            print("Rate limit alcanzado. Esperando 60 segundos...")
            time.sleep(60)
            return fetch_anilist_data(anime_id)
        time.sleep(2)
        
        data = response.json().get('data', {}).get('Media', {})
        if not data:
            return None
        
        episodios = data['episodes'] or 0
        duracion = data['duration'] or 24
        return {
            'nombre': data['title']['romaji'],
            'minutos': episodios * duracion,
            'score': (data['averageScore'] / 100) if data['averageScore'] else 0            
        }
    except Exception as e:
        print(f"Error en request: {e}")
        return None
        

def calcular_coeficiente(fila_ids):
    nombre_display = ""
    minutos_totales = 0
    score_ponderado = 0
    
    for i, anime_id in enumerate(fila_ids):
        data = fetch_anilist_data(int(anime_id))
        if not data:
            continue
        
        if i == 0:
            nombre_display = data['nombre']
        
        minutos_totales += data['minutos']
        score_ponderado += data['minutos'] * data['score']
        
    if minutos_totales == 0:
        print(f"{nombre_display} no tiene duración valida")
        return None, None
    
    minutos_totales = max(minutos_totales, 120)
    
    val_score_final = score_ponderado / minutos_totales
    val_min_final = 1 / (1 + 0.625 * math.log(minutos_totales / ESTANDAR_MINUTOS))
    
    coef = (val_score_final * PORCENTAJE_SCORE) + (val_min_final * (1 - PORCENTAJE_SCORE))
    
    return nombre_display, coef

def procesar_lista(ruta_entrada, ruta_salida):
    with open (ruta_entrada, newline="", encoding="utf-8") as archivo_entrada, \
        open (ruta_salida, 'w', newline="", encoding="utf-8") as archivo_salida:
            
        total_filas = sum(1 for _ in archivo_entrada)
        archivo_entrada.seek(0)
            
        reader = csv.reader(archivo_entrada)
        writer = csv.writer(archivo_salida)
        
        for i, fila in enumerate(reader, start=1):
            if not fila:
                
                continue
            print(f"Procesando: {i}/{total_filas}")
            nombre, coeficiente = calcular_coeficiente(fila)
            
            if coeficiente:
                writer.writerow([nombre, coeficiente])
    
    print(f"\nArchivo de salida generado: {ruta_salida}")
   
if __name__ == "__main__":
    ruta_base = os.path.dirname(__file__)
    ruta_entrada = os.path.join(ruta_base, 'animes_input.csv')
    ruta_salida = os.path.join(ruta_base, 'animes_output.csv')
    
    procesar_lista(ruta_entrada, ruta_salida)
