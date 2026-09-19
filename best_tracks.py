import urllib.request

HURDAT_URL = "https://www.nhc.noaa.gov/data/hurdat/hurdat2-1851-2025-091226.txt"


def descargar_hurdat():
    with urllib.request.urlopen(HURDAT_URL) as response:
        return response.read().decode("utf-8")


def buscar_ciclon(texto, nombre):
    lineas = texto.splitlines()

    for i, linea in enumerate(lineas):
        partes = linea.split(",")

        if len(partes) >= 2:
            identificador = partes[0].strip()
            nombre_ciclon = partes[1].strip()

            if nombre_ciclon.upper() == nombre.upper():
                cantidad_posiciones = int(partes[2].strip())

                return lineas[i:i + cantidad_posiciones + 1]

    return []
