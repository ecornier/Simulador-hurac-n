import urllib.request

HURDAT_URL = "https://www.nhc.noaa.gov/data/hurdat/hurdat2-1851-2025-091226.txt"


def descargar_hurdat():
    with urllib.request.urlopen(HURDAT_URL) as response:
        return response.read().decode("utf-8")


def buscar_ciclon(texto, nombre):
    lineas = texto.splitlines()

    for i, linea in enumerate(lineas):
        if nombre.upper() in linea.upper():
            return lineas[i:i + 10]

    return []


if __name__ == "__main__":
    datos = descargar_hurdat()

    maria = buscar_ciclon(datos, "MARIA")

    print("Datos encontrados:")
    for linea in maria:
        print(linea)
