import requests
import datetime
import json
import os 

# URL da API do USGS 
URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"

magnitudeMinima = 4.5
PASTA_PINS = "pins" 

def formatarData(timestamp_ms):
    """Converte milissegundos em tempo legivel."""
    data_obj = datetime.datetime.fromtimestamp(timestamp_ms / 1000)
    return data_obj.strftime('%d/%m/%Y | %H:%M')

def gerar_kml_versionado(lista_terremotos):
    """Gera o arquivo KML numerado na pasta pins"""
    
    # Cria a pasta se não existir
    if not os.path.exists(PASTA_PINS):
        os.makedirs(PASTA_PINS)
        print(f"📁 Pasta '{PASTA_PINS}' criada.")

    # Lógica de Versionamento 
    contador_arq = 1
    while True:
        nome_arquivo = os.path.join(PASTA_PINS, f"terremotos_{contador_arq:03d}.kml")
        if not os.path.exists(nome_arquivo):
            break 
        contador_arq += 1


    # conteúdo do KML
    kml_content = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<kml xmlns="http://www.opengis.net/kml/2.2">',
        '<Document>',
        f'<name>Monitoramento Sísmico #{contador_arq}</name>'
    ]

    for tremor in lista_terremotos:
        props = tremor['properties']
        coords = tremor['geometry']['coordinates']
        
        # O KML precisa de: Longitude, Latitude (nessa ordem)
        placemark = f"""
        <Placemark>
            <name>Mag {props['mag']} - {props['place']}</name>
            <description>Data: {formatarData(props['time'])}\nLink: {props['url']}</description>
            <Point>
                <coordinates>{coords[0]},{coords[1]}</coordinates>
            </Point>
        </Placemark>
        """
        kml_content.append(placemark)

    kml_content.append('</Document>\n</kml>')

    # 4. Salva o arquivo
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write("".join(kml_content))
    
    print(f"✅ Arquivo salvo com sucesso em: {nome_arquivo}")


def buscar_terremotos():
    print("🌊 Navegando até os dados da USGS...")
    print(f"🌊 Varrendo o globo por tremores acima de {magnitudeMinima} Mag...\n")
    
    try:
        response = requests.get(URL)
        
        if response.status_code == 200:
            dados = response.json()
            totalBruto = dados['metadata']['count']
            print(f"total de tremores bruto (sem filtro): {totalBruto}")
            lista_terremotos = dados['features']
            
            contador = 0
            tremores_para_kml = [] # Lista auxiliar para guardar os dados pro mapa
            
            for tremor in lista_terremotos:
                props = tremor['properties']
                geometry = tremor['geometry']
                
                mag = props['mag']
                
                # AQUI É O FILTRO: Só mostra se for maior ou igual a 4.5
                if mag >= magnitudeMinima:
                    contador += 1
                    local = props['place']
                    data_formatada = formatarData(props['time'])
                    coords = geometry['coordinates'] # [Longitude, Latitude, Profundidade]
                    link = props['url'] # Link para ver no mapa do USGS
                    
                    # Guarda este tremor na lista do KML
                    tremores_para_kml.append(tremor)
                    
                    # Exibição Formatada
                    print("-" * 50)
                    print(f"🚨 ALERTA SÍSMICO #{contador}")
                    print(f"📉 Magnitude: {mag}")
                    print(f"📍 Local: {local}")
                    print(f"🕒 Data/Hora: {data_formatada}")
                    print(f"🧭 Coordenadas: Lat {coords[1]}, Long {coords[0]}")
                    print(f"🌊 Profundidade: {coords[2]} km")
                    print(f"🔗 Link: {link}")
            
            print("-" * 50)
            if contador == 0:
                print("✅ Nenhum tremor grave detectado neste período.")
            else:
                print(f"⚠️ Total de eventos críticos encontrados: {contador}")
                # Se achou algo, gera o mapa!
                gerar_kml_versionado(tremores_para_kml)
                
        else:
            print(f"❌ Erro na conexão: {response.status_code}")
            
    except Exception as e:
        print(f"☠️ Erro crítico no sistema: {e}")

if __name__ == "__main__":
    buscar_terremotos()
    input("\n✅ Pressione ENTER para fechar o radar...")