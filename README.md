# anime-recommender

Sistema personal para elegir qué anime ver, basado en la lista de AniList del usuario.

## ¿Qué hace?

1. **Importa tu lista** de AniList (estado "Plan to Watch"), agrupa sagas completas (secuelas y precuelas) y genera un archivo de entrada.
2. **Calcula un coeficiente** para cada anime o saga, combinando su valoración promedio (70%) y su duración total (30%).
3. **Elige un anime al azar** respetando esos coeficientes como pesos — los mejor puntuados y más cortos tienen más chances.

## Requisitos

- Python 3.10+
- Cuenta en [AniList](https://anilist.co)

## Uso

Corré los scripts en orden:

```bash
python importar_lista.py
python calcular_coeficiente.py
python eleccion_random.py
```

Cada vez que quieras una recomendación fresca, solo corré `eleccion_random.py`.
Volvé a correr los tres si tu lista de AniList cambió.

## Estructura

```text
anime-recommender/
├── importar_lista.py        # Importa y agrupa sagas desde AniList
├── calcular_coeficiente.py  # Calcula el coeficiente de cada saga
├── eleccion_random.py       # Elige un anime al azar con pesos
├── animes_input.csv         # Generado por importar_lista.py
└── animes_output.csv        # Generado por calcular_coeficiente.py
```
