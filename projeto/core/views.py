# Bibliotecas padrão
import json
import traceback
from typing import List, Dict, Any

# Bibliotecas de terceiros
import requests
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.http import HttpResponseBadRequest, HttpResponseNotAllowed, JsonResponse, HttpResponseServerError
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

# Módulos locais
from .forms import RegistroSimplesForm, RegistroCompletoForm, EnderecoForm
from .models import RegistroCompleto, RegistroSimples, Endereco
from .utils import get_lat_lon_from_address, get_address_from_cep

# Selenium (considerar mover para um serviço separado)
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
@login_required
def home(request):
    return render(request, 'home.html')
  
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('/')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('/login/')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()
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
        form = RegistroSimplesForm()
        endereco_form = EnderecoForm()
    return render(request, 'registro_simples.html', {'form': form, 'endereco_form': endereco_form})

def registro_completo(request):
    if request.method == 'POST':
        form = RegistroCompletoForm(request.POST)
        endereco_form = EnderecoForm(request.POST)
        if form.is_valid() and endereco_form.is_valid():
            endereco = handle_endereco_form(endereco_form)
            registro = form.save(commit=False)
            registro.endereco = endereco
            registro.save()
            return redirect('home')
    else:
        form = RegistroCompletoForm()
        endereco_form = EnderecoForm()
    return render(request, 'registro_completo.html', {'form': form, 'endereco_form': endereco_form})

@login_required
def visualizar_registros_simples(request):
    registros = RegistroSimples.objects.all()
    return render(request, 'visualizar_registros_simples.html', {'registros': registros})

def visualizar_registros_completos(request):
    registros = RegistroCompleto.objects.all()
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
        form = RegistroSimplesForm(instance=registro)
        endereco_form = EnderecoForm(instance=registro.endereco)
    return render(request, 'editar_registro_simples.html', {'form': form, 'endereco_form': endereco_form})

@login_required
def editar_registro_completo(request, pk):
    registro = get_object_or_404(RegistroCompleto, pk=pk)
    if request.method == 'POST':
        form = RegistroCompletoForm(request.POST, instance=registro)
        endereco_form = EnderecoForm(request.POST, instance=registro.endereco)
        if form.is_valid() and endereco_form.is_valid():
            endereco = endereco_form.save(commit=False)
            endereco.save()
            form.save()
            return redirect('visualizar_registros_completos')
    else:
        form = RegistroCompletoForm(instance=registro)
        endereco_form = EnderecoForm(instance=registro.endereco)
    return render(request, 'editar_registro_completo.html', {'form': form, 'endereco_form': endereco_form})


@login_required
def excluir_registro_simples(request, pk):
    registro = get_object_or_404(RegistroSimples, pk=pk)

    # Exclui o endereço associado
    if registro.endereco:
        endereco = registro.endereco
        endereco.delete()

    # Exclui o registro simples
    registro.delete()

    return redirect('visualizar_registros_simples')

@login_required
def excluir_registro_completo(request, pk):
    registro = get_object_or_404(RegistroCompleto, pk=pk)

    # Exclui o endereço associado
    if registro.endereco:
        endereco = registro.endereco
        endereco.delete()

    # Exclui o registro completo
    registro.delete()

    return redirect('visualizar_registros_completos')

def preenche_formulario(request):
    if request.method == "POST":
        nome_titulo_cpf = request.POST.get("nome_titulo_cpf")
        data_nascimento = request.POST.get("data_nascimento")
        nome_mae = request.POST.get("nome_mae")

        data_nascimento = "/".join(reversed(data_nascimento.split("-")))

        service = ChromeService(executable_path=ChromeDriverManager().install())
        options = ChromeOptions()
        options.add_argument("--headless")  # Executa em modo headless (sem interface gráfica)

        driver = None  # Inicializa a variável driver fora do bloco try

        try:
            # Configura o ChromeDriver
            driver = Chrome(service=service, options=options)

            # Abre o site
            driver.get("https://www.tse.jus.br/servicos-eleitorais/titulo-e-local-de-votacao/titulo-e-local-de-votacao")

            # Aguarda a página carregar
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.NAME, "nomeTituloCPF"))
            )

            # Preenche os campos do formulário
            driver.find_element(By.NAME, "nomeTituloCPF").send_keys(nome_titulo_cpf)
            driver.find_element(By.NAME, "dataNascimento").send_keys(data_nascimento)
            driver.find_element(By.NAME, "nomeMae").send_keys(nome_mae)

            # Scroll para o botão Consultar
            element = driver.find_element(By.ID, "consultar-local-votacao-form-submit")
            driver.execute_script("arguments[0].scrollIntoView();", element)

            # Aguarda o botão Consultar estar clicável
            WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.ID, "consultar-local-votacao-form-submit"))
            )

            # Clica no botão Consultar
            element.click()

            # Aguarda a página de resultados carregar
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.ID, "return-form-local-votacao-cloud"))
            )

            # Exibir o elemento oculto
            driver.execute_script("document.getElementById('return-form-local-votacao-cloud').style.display = 'block';")

            # Aguarda os dados estarem visíveis
            WebDriverWait(driver, 30).until(
                EC.visibility_of_element_located((By.ID, "return-form-local-votacao-cloud"))
            )

            # Extrai dados da página resultante
            paragrafos = driver.find_elements(By.TAG_NAME, "p")

            cpf = ""
            eleitor = ""
            zona_secao = ""
            local = ""
            municipio = ""

            for paragrafo in paragrafos:
                texto = paragrafo.text.strip()

                if texto.startswith("CPF:"):
                    cpf = texto.split(":")[1].strip()
                elif texto.startswith("Eleitor:"):
                    eleitor = texto.split(":")[1].strip()
                elif texto.startswith("Zona:"):
                    zona_secao = texto.strip()
                elif texto.startswith("Local:"):
                    local = texto.split(":")[1].strip()
                elif texto.startswith("Município:"):
                    municipio = texto.split(":")[1].strip()

            # Formata o resultado como HTML
            resultado = f"""
            <h2>IDENTIFICAÇÃO</h2>
            <p>CPF: {cpf}</p>
            <p>Eleitor: {eleitor}</p>
            <h2>DOMICÍLIO ELEITORAL</h2>
            <p>{zona_secao}</p>
            <p>Local: {local}</p>
            <p>Município: {municipio}</p>
            """

        except TimeoutException as e:
            resultado = f"Erro: Tempo de espera expirado. Detalhes: {str(e)}"
        except NoSuchElementException as e:
            resultado = f"Erro: Elemento não encontrado. Detalhes: {str(e)}"
        except Exception as e:
            resultado = f"Erro ao preencher o formulário: {str(e)}"
            traceback.print_exc()  # Mostra detalhes do erro no console para depuração

        finally:
            # Fecha o navegador
            if driver:
                driver.quit()

        return render(request, "resultado.html", {"resultado": resultado})

    return render(request, "preenche_formulario.html")


def resultado(request):
    return render(request, "resultado.html")


def buscar_cep_v2(cep):
    url = f"https://brasilapi.com.br/api/cep/v2/{cep}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except requests.RequestException as e:
        return None

Coordinate = Dict[str, float]
CoordinatesList = List[Coordinate]

@login_required
def visualizar_mapa(request):
    try:
        enderecos = Endereco.objects.all()
        coordenadas = []

        def adicionar_coordenadas(lat, lng, titulo):
            coordenadas.append({'lat': lat, 'lng': lng, 'titulo': titulo})

        for endereco in enderecos:
            try:
                cep_info = buscar_cep_v2(endereco.cep)
                if cep_info:
                    endereco_formatado = f"{cep_info['street']}, {endereco.numero}, {cep_info['neighborhood']}, {cep_info['city']}, {cep_info['state']}, {cep_info['cep']}"
                    lat, lng = get_lat_lon_from_address(endereco_formatado)
                    if lat is not None and lng is not None:
                        adicionar_coordenadas(lat, lng, f"Endereço: {endereco_formatado}")
            except Exception as e:
                continue  # Log error if necessary

        context = {
            'coordenadas': json.dumps(coordenadas),
            'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY
        }
        return render(request, 'visualizar_mapa.html', context)

    except Exception as e:
        return HttpResponseServerError(f"Erro ao processar a solicitação: {str(e)}")
    

@login_required
def atualizar_endereco(request):
    if request.method == 'POST':
        lat = request.POST.get('lat')
        lng = request.POST.get('lng')
        titulo = request.POST.get('titulo')

        try:
            endereco = get_object_or_404(Endereco, endereco_formatado=titulo)
            endereco.latitude = float(lat)
            endereco.longitude = float(lng)
            endereco.save()
            return JsonResponse({'message': 'Endereço atualizado com sucesso.'})
        except Exception as e:
            return HttpResponseServerError(f"Erro ao atualizar endereço: {str(e)}")
    else:
        return HttpResponseBadRequest("Requisição inválida ou método não permitido.")
    

@login_required
def salvar_novo_endereco(request):
    if request.method == 'POST':
        novo_endereco = request.POST.get('novo_endereco', None)
        if novo_endereco:
            try:
                endereco_salvo = Endereco.objects.create(endereco=novo_endereco)
                return HttpResponse(f"Novo endereço '{endereco_salvo.endereco}' salvo com sucesso.")
            except Exception as e:
                return HttpResponseServerError(f"Erro ao salvar o novo endereço: {str(e)}")
        else:
            return HttpResponseBadRequest("Dados inválidos ou ausentes.")
    else:
        return HttpResponseNotAllowed(['POST'], "Apenas o método POST é permitido para esta URL.")