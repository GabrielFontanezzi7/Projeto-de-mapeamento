# views.py

# Bibliotecas padrão
import json
import logging
from datetime import datetime
import traceback
from typing import List, Dict, Any

# Bibliotecas de terceiros
import requests
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.http import HttpResponseBadRequest, HttpResponseNotAllowed, JsonResponse, HttpResponseServerError
from django.conf import settings
from django.db.models import Q, Count
from django.contrib.auth.models import User
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages


# Módulos locais
from .forms import RegistroSimplesForm, RegistroCompletoForm, EnderecoForm, CustomUserCreationForm
from .models import RegistroCompleto, RegistroSimples, Endereco
from .utils import get_lat_lon_from_address, get_address_from_cep, enderecos_para_json
from .models import CustomUser, RegistroSimples, RegistroCompleto

# Selenium (considerar mover para um serviço separado)
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver

logger = logging.getLogger(__name__)


def logout_view(request):
    logout(request)
    return redirect('login')

def is_admin(user):
    return user.is_admin



def home(request):
    registros_completos = RegistroCompleto.objects.all()
    registros_simples = RegistroSimples.objects.all()
    total_registros_completos = registros_completos.count()
    total_registros_simples = registros_simples.count()
    
    locais_votacao = (registros_completos.values('local', 'municipio', 'endereco_votacao')
                      .annotate(count=Count('local'))
                      .order_by('-count'))

    total_locais_votacao = locais_votacao.count()

    locais_votacao_list = list(locais_votacao)
    locais_votacao_json = json.dumps(locais_votacao_list, ensure_ascii=False)

    context = {
        'total_registros_simples': total_registros_simples,
        'total_registros_completos': total_registros_completos,
        'total_locais_votacao': total_locais_votacao,
        'locais_votacao': locais_votacao_list,
        'locais_votacao_json': locais_votacao_json,
        'outras_informacoes': 'Adicione outras informações aqui',
        'google_maps_api_key':"AIzaSyCAJrVf6a2fw_Eb_vUwqXgJcpRN0D9qxsk"
    }

    return render(request, 'home.html', context)

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(request, username=username_or_email, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('/')
            else:
                messages.error(request, 'Invalid username/email or password')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Salva o novo usuário no banco de dados
            messages.success(request, "Registro realizado com sucesso. Faça login para continuar.")
            return redirect('login')  # Redireciona para a página de login
        else:
            messages.error(request, "Erro ao registrar. Verifique as informações e tente novamente.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def handle_endereco_form(endereco_form):
    endereco = endereco_form.save(commit=False)
    address_data = get_address_from_cep(endereco.cep)
    if address_data:
        endereco.rua = address_data.get('street', endereco.rua)
        endereco.bairro = address_data.get('neighborhood', endereco.bairro)
        endereco.cidade = address_data.get('city', endereco.cidade)
        endereco.estado = address_data.get('state', endereco.estado)
        endereco.save()
        endereco.endereco_formatado = f"{endereco.rua}, {endereco.numero}, {endereco.bairro}, {endereco.cidade}, {endereco.estado}"
        lat, lon = get_lat_lon_from_address(endereco.endereco_formatado)
        endereco.latitude = lat
        endereco.longitude = lon
        endereco.save()
    return endereco

def registro_simples(request):
    if request.method == 'POST':
        form = RegistroSimplesForm(request.POST)
        endereco_form = EnderecoForm(request.POST)
        if form.is_valid() and endereco_form.is_valid():
            endereco = handle_endereco_form(endereco_form)
            registro = form.save(commit=False)
            registro.endereco = endereco
            registro.save()
            return redirect('home')
        else:
            messages.error(request, "Error in form submission.")
    else:
        form = RegistroSimplesForm()
        endereco_form = EnderecoForm()
    return render(request, 'registro_simples.html', {'form': form, 'endereco_form': endereco_form})

def registro_completo(request):
    if request.method == 'POST':
        form = RegistroCompletoForm(request.POST)
        endereco_form = EnderecoForm(request.POST)
        if form.is_valid() and endereco_form.is_valid():
            endereco = endereco_form.save(commit=False)
            endereco.save()
            registro = form.save(commit=False)
            registro.endereco = endereco
            # Dividir o campo combinado em zona e secao
            zona_secao = request.POST.get('zona_secao', '')
            if " Seção: " in zona_secao:
                registro.zona, registro.secao = zona_secao.replace("Zona: ", "").split(" Seção: ")
            else:
                registro.zona = zona_secao.replace("Zona: ", "")
                registro.secao = ""
            registro.save()
            messages.success(request, "Registro completo salvo com sucesso.")
            return redirect('home')
        else:
            messages.error(request, "Erro no envio do formulário.")
    else:
        form = RegistroCompletoForm()
        endereco_form = EnderecoForm()

    context = {
        'form': form,
        'endereco_form': endereco_form
    }

    return render(request, 'registro_completo.html', context)

@login_required
def visualizar_registros_simples(request):
    registros = RegistroSimples.objects.select_related('endereco').all()
    return render(request, 'visualizar_registros_simples.html', {'registros': registros})

@login_required
def visualizar_registros_completos(request):
    registros = RegistroCompleto.objects.select_related('endereco').all()
    return render(request, 'visualizar_registros_completos.html', {'registros': registros})


@login_required
def editar_registro_simples(request, pk): 
    registro = get_object_or_404(RegistroSimples, pk=pk)
    if request.method == 'POST':
        form = RegistroSimplesForm(request.POST, instance=registro)
        endereco_form = EnderecoForm(request.POST, instance=registro.endereco)
        if form.is_valid() and endereco_form.is_valid():
            endereco = endereco_form.save(commit=False)
            endereco.save()
            form.save()
            return redirect('visualizar_registros_simples')
        else:
            messages.error(request, "Error in form submission.")
    else:
        form = RegistroSimplesForm(instance=registro)
        endereco_form = EnderecoForm(instance=registro.endereco)
    return render(request, 'editar_registro_simples.html', {'form': form, 'endereco_form': endereco_form})



@login_required
def editar_registro_completo(request, pk):
    
    registro = get_object_or_404(RegistroCompleto, pk=pk)
    registros_simples = RegistroSimples.objects.all()
    registros_completos = RegistroCompleto.objects.all()
    
    if request.method == 'POST':
        form = RegistroCompletoForm(request.POST, instance=registro)
        endereco_form = EnderecoForm(request.POST, instance=registro.endereco)
        if form.is_valid() and endereco_form.is_valid():
            endereco = endereco_form.save(commit=False)
            endereco.save()
            registro = form.save(commit=False)
            # Dividir o campo combinado em zona e secao
            zona_secao = request.POST.get('zona_secao', '')
            if " Seção: " in zona_secao:
                registro.zona, registro.secao = zona_secao.replace("Zona: ", "").split(" Seção: ")
            else:
                registro.zona = zona_secao.replace("Zona: ", "")
                registro.secao = ""
            registro.save()
            return redirect('visualizar_registros_completos')
        else:
            messages.error(request, "Erro no envio do formulário.")
    else:
        form = RegistroCompletoForm(instance=registro)
        endereco_form = EnderecoForm(instance=registro.endereco)
    
    context = {
        'form': form,
        'endereco_form': endereco_form,
        'registro': registro,
        'registros_simples': registros_simples,
        'registros_completos': registros_completos
    }
    
    return render(request, 'editar_registro_completo.html', context)

@login_required
def excluir_registro_simples(request, pk):
    registro = get_object_or_404(RegistroSimples, pk=pk)
    if registro.endereco:
        endereco = registro.endereco
        endereco.delete()
    registro.delete()
    return redirect('visualizar_registros_simples')

@login_required
def excluir_registro_completo(request, pk):
    registro = get_object_or_404(RegistroCompleto, pk=pk)
    if registro.endereco:
        endereco = registro.endereco
        endereco.delete()
    registro.delete()
    return redirect('visualizar_registros_completos')

def preencher_formulario(cpf, data_nascimento, nome_mae):
    try:
        if '-' in data_nascimento:
            data_nascimento = datetime.strptime(data_nascimento, '%Y-%m-%d').strftime('%d/%m/%Y')

        service = ChromeService(executable_path=ChromeDriverManager().install())
        options = ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(service=service, options=options)
        try:
            driver.get("https://www.tse.jus.br/servicos-eleitorais/titulo-e-local-de-votacao/titulo-e-local-de-votacao")

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "nomeTituloCPF"))
            )

            driver.find_element(By.NAME, "nomeTituloCPF").send_keys(cpf)
            driver.find_element(By.NAME, "dataNascimento").send_keys(data_nascimento)
            driver.find_element(By.NAME, "nomeMae").send_keys(nome_mae)

            element = driver.find_element(By.ID, "consultar-local-votacao-form-submit")
            driver.execute_script("arguments[0].scrollIntoView();", element)

            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "consultar-local-votacao-form-submit"))
            )

            element.click()

            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "return-form-local-votacao-cloud"))
            )

            driver.execute_script("document.getElementById('return-form-local-votacao-cloud').style.display = 'block';")

            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "return-form-local-votacao-cloud"))
            )

            paragrafos = driver.find_elements(By.TAG_NAME, "p")

            resultado = {
                "zona": "",
                "secao": "",
                "municipio": "",
                "local": "",
                "endereco_votacao": ""
            }

            for paragrafo in paragrafos:
                texto = paragrafo.text.strip()

                if texto.startswith("Zona:"):
                    partes = texto.split("Seção:")
                    if len(partes) == 2:
                        resultado["zona"] = partes[0].split(":")[1].strip()
                        resultado["secao"] = partes[1].strip()
                elif texto.startswith("Município:"):
                    resultado["municipio"] = texto.split(":")[1].strip()
                elif texto.startswith("Local:"):
                    resultado["local"] = texto.split(":")[1].strip()
                elif texto.startswith("Endereço:"):
                    resultado["endereco_votacao"] = texto.split(":")[1].strip()

            return resultado

        except TimeoutException as e:
            logger.error(f"Erro: Tempo de espera expirado. Detalhes: {str(e)}")
            return {"error": f"Erro: Tempo de espera expirado. Detalhes: {str(e)}"}
        except NoSuchElementException as e:
            logger.error(f"Erro: Elemento não encontrado. Detalhes: {str(e)}")
            return {"error": f"Erro: Elemento não encontrado. Detalhes: {str(e)}"}
        except WebDriverException as e:
            logger.error(f"Erro ao conectar: {str(e)}")
            return {"error": f"Erro ao conectar: {str(e)}"}
        except Exception as e:
            logger.error(f"Erro ao preencher o formulário: {str(e)}")
            traceback.print_exc()
            return {"error": f"Erro ao preencher o formulário: {str(e)}"}
        finally:
            driver.quit()
    except Exception as e:
        logger.error(f"Erro ao processar a data de nascimento: {str(e)}")
        traceback.print_exc()
        return {"error": f"Erro ao processar a data de nascimento: {str(e)}"}
    
@csrf_exempt
@login_required
def preencher_formulario_ajax(request):
    if request.method == 'POST':
        cpf = request.POST.get('cpf')
        data_nascimento = request.POST.get('data_nascimento')
        nome_mae = request.POST.get('nome_mae')
        resultado = preencher_formulario(cpf, data_nascimento, nome_mae)
        if 'error' in resultado:
            return JsonResponse({'status': 'error', 'message': resultado['error']})
        return JsonResponse({
            'status': 'success',
            'zona': resultado.get('zona', ''),
            'secao': resultado.get('secao', ''),
            'municipio': resultado.get('municipio', ''),
            'local': resultado.get('local', ''),
            'endereco_votacao': resultado.get('endereco_votacao', '')
        })
    return JsonResponse({'status': 'error', 'message': 'Método inválido'})

  
    

def visualizar_mapa(request):
    enderecos_simples = Endereco.objects.filter(registros_simples__isnull=False)
    enderecos_completos = Endereco.objects.filter(registros_completos__isnull=False)

    context = {
        'coordenadas_simples': enderecos_para_json(enderecos_simples),
        'coordenadas_completas': enderecos_para_json(enderecos_completos),
        'registros_simples': RegistroSimples.objects.all(),
        'registros_completos': RegistroCompleto.objects.all(),
        'google_maps_api_key': 'AIzaSyCAJrVf6a2fw_Eb_vUwqXgJcpRN0D9qxsk'
    }
    
    return render(request, 'visualizar_mapa.html', context)

@csrf_exempt
@login_required
def atualizar_endereco(request):
    if request.method == 'POST':
        try:
            logger.info("Recebendo dados da requisição para atualizar endereço.")
            data = json.loads(request.body)
            endereco_id = data.get('id')
            lat = data.get('lat')
            lng = data.get('lng')

            logger.info(f"Dados recebidos: ID: {endereco_id}, Lat: {lat}, Lng: {lng}")

            if not endereco_id or lat is None or lng is None:
                logger.error(f"Dados inválidos recebidos: {data}")
                return JsonResponse({'status': 'error', 'message': 'Dados inválidos recebidos'})

            try:
                endereco_antigo = Endereco.objects.get(id=endereco_id)
            except Endereco.DoesNotExist:
                logger.error(f"Endereço com ID {endereco_id} não encontrado")
                return JsonResponse({'status': 'error', 'message': 'Endereço não encontrado'})

            logger.info(f"Endereço antigo encontrado: {endereco_antigo}")

            # Criando um novo endereço
            novo_endereco = Endereco.objects.create(
                cep=endereco_antigo.cep,
                rua=endereco_antigo.rua,
                numero=endereco_antigo.numero,
                bairro=endereco_antigo.bairro,
                cidade=endereco_antigo.cidade,
                estado=endereco_antigo.estado,
                latitude=lat,
                longitude=lng
            )
            
            novo_endereco.endereco_formatado = f"{novo_endereco.rua}, {novo_endereco.numero}, {novo_endereco.bairro}, {novo_endereco.cidade}, {novo_endereco.estado}"
            novo_endereco.save()

            logger.info(f"Novo endereço criado: {novo_endereco}")

            # Atualizando a referência no registro simples e completo
            registros_simples = RegistroSimples.objects.filter(endereco=endereco_antigo)
            registros_completos = RegistroCompleto.objects.filter(endereco=endereco_antigo)
            
            for registro in registros_simples:
                registro.endereco = novo_endereco
                registro.save()
                logger.info(f"Registro simples atualizado: {registro}")

            for registro in registros_completos:
                registro.endereco = novo_endereco
                registro.save()
                logger.info(f"Registro completo atualizado: {registro}")

            # Excluindo o endereço antigo
            endereco_antigo.delete()
            logger.info(f"Endereço antigo excluído: {endereco_antigo}")

            return JsonResponse({
                'status': 'success',
                'message': 'Endereço atualizado com sucesso',
                'endereco': novo_endereco.endereco_formatado
            })
        except json.JSONDecodeError:
            logger.error("Erro ao decodificar JSON")
            return JsonResponse({'status': 'error', 'message': 'Erro ao decodificar JSON'})
        except Exception as e:
            logger.error(f"Erro ao atualizar endereço: {str(e)}")
            return JsonResponse({'status': 'error', 'message': f"Erro ao atualizar endereço: {str(e)}"})
    else:
        return JsonResponse({'status': 'error', 'message': 'Método não permitido'})
    

def lista_registros(request):
    registros_completos = RegistroCompleto.objects.all()
    registros_simples = RegistroSimples.objects.all()
    return render(request, 'lista_registros.html', {
        'registros_completos': registros_completos,
        'registros_simples': registros_simples
    })

def lista_registros_json(request):
    registros_completos = RegistroCompleto.objects.all().select_related('endereco')
    registros_simples = RegistroSimples.objects.all().select_related('endereco')

    registros = [
        {
            'nome': registro.nome,
            'endereco': registro.endereco.endereco_formatado,
            'latitude': registro.endereco.latitude,
            'longitude': registro.endereco.longitude,
            'tipo': 'completo'
        }
        for registro in registros_completos
    ] + [
        {
            'nome': registro.nome,
            'endereco': registro.endereco.endereco_formatado,
            'latitude': registro.endereco.latitude,
            'longitude': registro.endereco.longitude,
            'tipo': 'simples'
        }
        for registro in registros_simples
    ]

    return JsonResponse(registros, safe=False)

@login_required
def atualizar_registros_completos(request):
    registros = RegistroCompleto.objects.filter(
        zona__isnull=True,
        secao__isnull=True
    )

    for registro in registros:
        resultado = preencher_formulario(
            nome_titulo_cpf=registro.nome,
            data_nascimento=str(registro.data_nascimento),
            nome_mae=registro.nome_mae
        )

        if "error" in resultado:
            logger.error(f"Erro ao preencher o formulário para o registro {registro.id}: {resultado['error']}")
            continue

        registro.titulo_eleitor = resultado.get("eleitor")
        registro.zona = resultado.get("zona")
        registro.local = resultado.get("local")
        registro.municipio = resultado.get("municipio")
        registro.save()
        logger.info(f"Registro {registro.id} atualizado com sucesso.")

    return JsonResponse({"status": "success", "message": "Registros completos atualizados com sucesso."})

