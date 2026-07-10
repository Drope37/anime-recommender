import csv
import os
import requests
import time
from dotenv import load_dotenv
from collections import defaultdict

ANILIST_URL = 'https://graphql.anilist.co'


def anilist_request(query, variables):
    '''Hace un request a la API de Anilist con manejo de rate limit'''
    while True:
        try:
            response = requests.post(ANILIST_URL, json={'query': query, 'variables': variables})
            if response.status_code == 429:
                print("Rate limit alcanzado. Esperando 60 segundos...")
                time.sleep(60)
                continue
            time.sleep(1.5)
            return response.json()
        except Exception as e:
            print(f"Error en request: {e}")
            return None
        

def fetch_user_list(username, status):
    '''Trae los animes del usuario según el estado indicado (PLANNING, COMPLETED, etc.)'''
    query = '''
    query ($username: String, $status: MediaListStatus) {
        MediaListCollection(userName: $username, type: ANIME, status: $status) {
            lists { entries { media {
                        id
                        title { romaji }
                        status
                    }
                }
            }
        }
    }
    '''
    
    animes = {}
    
    data = anilist_request(query, {'username': username, 'status': status})
        
    entries = data['data']['MediaListCollection']['lists'][0]['entries']
    for entry in entries:
        media = entry['media']
        if media['status'] == 'FINISHED':
            animes[media['id']] = media['title']['romaji']
        
    return animes


def fetch_planning_list(username):
    '''Trae los animes en Planning, filtrando los no finalizados'''
    print(f"Buscando lista Planning...")
    todos = fetch_user_list(username, 'PLANNING')    
    print(f"    {len(todos)} animes encontrados\n")
    return todos


def fetch_completed_ids(username):
    '''Trae los IDs de todos los animes completados por el usuario'''
    print(f"Obteniendo lista Completed...")
    completados = fetch_user_list(username, 'COMPLETED')
    print(f"    {len(completados)} animes completados encontrados\n")
    return set(completados.keys())


def buscar_relaciones(anime_id_inicial):
    '''
    Recorre toda la cadena de secuelas y precuelas a partir de un anime,
    sin importar si estan en la lista del usuario. Devuelve todos los IDs
    de la saga
    '''
    query = '''
    query ($idAnime: Int) {
        Media(id: $idAnime) {
            relations {
                edges {
                    relationType
                    node {
                        id
                        status
                    }
                }
            }
            startDate { year month day }
        }
    }
    '''
    
    recorridos = set()
    incluidos = {}
    por_visitar = [anime_id_inicial]
    
    while por_visitar:
        anime_id = por_visitar.pop()
        if anime_id in recorridos:
            continue
        recorridos.add(anime_id)
    
        data = anilist_request(query, {'idAnime': anime_id})
        if not data:
            continue
            
        media = data.get('data', {}).get('Media', {})
        if not media:
            continue
        incluidos[anime_id] = media['startDate']
        
        edges = media.get('relations', {}).get('edges', [])
        for edge in edges:
            if edge['node']['status'] == 'FINISHED' and edge['relationType'] in ('SEQUEL', 'PREQUEL'):
                node = edge['node']
                if node['id'] not in recorridos:
                    por_visitar.append(node['id'])
    
    return incluidos


def agrupar_saga(animes, completados):
    '''
    Para cada anime en la lista del usuario, recorre su saga completa
    Al armar el grupo de IDs, excluye aquellos que el usuario ya vió
    '''
    ids_animes = set(animes.keys())
    
    print('Buscando sagas completas...')
    
    saga_por_anime = {}
    ya_en_saga = set()
    
    for i, anime_id in enumerate(ids_animes, 1):
        if anime_id in ya_en_saga:
            continue
        print(f'    ({i}/{len(ids_animes)}) {animes[anime_id]}')
        saga_completa = buscar_relaciones(anime_id)
        saga_por_anime[anime_id] = {k: v for k, v in saga_completa.items() if k not in completados}
        ya_en_saga.update(saga_completa)
        
    parent = {id_: id_ for id_ in saga_por_anime.keys()}
    
    def find_root(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    
    def union(x, y):
        parent[find_root(x)] = find_root(y)
    
    ids_lista = list(saga_por_anime.keys())
    for i in range(len(ids_lista)):
        for j in range(i + 1, len(ids_lista)):
            a, b = ids_lista[i], ids_lista[j]
            if saga_por_anime[a].keys() & saga_por_anime[b].keys():
                union(a, b)
            
    grupos_ids = defaultdict(dict)
    for anime_id in saga_por_anime.keys():
        raiz = find_root(anime_id)
        grupos_ids[raiz].update(saga_por_anime[anime_id])
    
    print(f"\n  {len(grupos_ids)} sagas formadas\n")    
    return grupos_ids


def guardar_sagas(grupos_ids, archivo_salida):
    '''
    Guarda las sagas en animes_input.csv
    '''
    with open(archivo_salida, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        for raiz, saga in grupos_ids.items():
            lista_ordenada = sorted(saga, key=lambda id: (saga[id]['year'], saga[id]['month'], saga[id]['day']))
            writer.writerow(lista_ordenada)


def main():
    username = 'Drope37'
    ruta_base = os.path.dirname(__file__)
    output_path = os.path.join(ruta_base, 'animes_input.csv')
    
    animes = fetch_planning_list(username)
    if not animes:
        print('No se encontraron animes. Verifique nombre de usuario o su lista de PLANNING')
        return
    
    completados = fetch_completed_ids(username)
    grupos_ids = agrupar_saga(animes, completados)
    guardar_sagas(grupos_ids, output_path)
    print(f"\nListo, ahora podes correr Coeficiente.py para calcular los coeficientess")

if __name__ == '__main__':
    main()
