from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
import requests
import json


def get_lat_lon_from_address(address):
    try:
        endpoint = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": address,
            "key": settings.GOOGLE_MAPS_API_KEY
        }
        response = requests.get(endpoint, params=params)
        response.raise_for_status()

        geocode_result = response.json()
        if geocode_result['status'] == 'OK':
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
    return None

def enderecos_para_json(enderecos):
    enderecos_list = []
    for endereco in enderecos:
        endereco_dict = {
            'id': endereco.id,
            'latitude': endereco.latitude,
            'longitude': endereco.longitude,
            'endereco_formatado': endereco.endereco_formatado,
            'nome': endereco.registros_simples.first().nome if endereco.registros_simples.exists() else endereco.registros_completos.first().nome,
            # Adicione outros campos de endereço conforme necessário
        }
        enderecos_list.append(endereco_dict)
    
    return json.dumps(enderecos_list)
