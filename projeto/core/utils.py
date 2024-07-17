from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
import requests
import json


def get_lat_lon_from_address(address):
    try:
        # Montar a URL para a solicitação da API do Google Maps
        endpoint = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": address,
            "key": settings.GOOGLE_MAPS_API_KEY
        }
        response = requests.get(endpoint, params=params)
        response.raise_for_status()  # Levanta uma exceção para códigos de status HTTP ruins

        # Parse do JSON de resposta
        geocode_result = response.json()
        if geocode_result['status'] == 'OK':
            # Pega a primeira resposta de geocodificação
            location = geocode_result['results'][0]['geometry']['location']
            return location['lat'], location['lng']
        else:
            print(f"Erro na geocodificação: {geocode_result['status']}")
            return None, None
    except requests.RequestException as e:
        print(f"Erro na solicitação da API do Google Maps: {str(e)}")
        return None, None

    
def get_address_from_cep(cep):
    response = requests.get(f'https://brasilapi.com.br/api/cep/v1/{cep}')
    if response.status_code == 200:
        return response.json()
    return 

def enderecos_para_json(enderecos):
    """
    Converte uma lista de objetos de endereço em uma string JSON válida.
    Cada objeto de endereço deve ser um dicionário Python.
    """
    enderecos_list = []
    for endereco in enderecos:
        endereco_dict = {
            'latitude': endereco.latitude,
            'longitude': endereco.longitude,
            'endereco': endereco.endereco,
            # Adicione outros campos de endereço conforme necessário
        }
        enderecos_list.append(endereco_dict)
    
    return json.dumps(enderecos_list)

