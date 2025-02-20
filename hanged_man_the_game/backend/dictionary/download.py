import requests

url = "https://raw.githubusercontent.com/CSL-LABS/CrackingWordLists/refs/heads/master/dics/lang/spanish_es_AR.dic"

respuesta = requests.get(url)

if respuesta.status_code == 200:
    with open("diccionario.txt", "w", encoding="utf-8") as archivo:
        archivo.write(respuesta.text)
    print("Archivo 'diccionario.txt' descargado y guardado correctamente.")
else:
    print("Error al descargar el archivo.")

with open("diccionario.txt", "r", encoding="utf-8") as archivo:
    palabras = archivo.readlines()

print("Primeras 100 palabras del diccionario:")
print(palabras[:100])