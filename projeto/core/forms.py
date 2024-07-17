from django import forms
from .models import RegistroSimples, RegistroCompleto, Endereco

class EnderecoForm(forms.ModelForm):
    class Meta:
        model = Endereco
        fields = ['cep', 'rua', 'numero', 'bairro', 'cidade', 'estado']


class RegistroSimplesForm(forms.ModelForm):
    class Meta:
        model = RegistroSimples
        fields = ['nome', 'email', 'telefone', 'cpf', 'data_nascimento']
       
class RegistroCompletoForm(forms.ModelForm):
    class Meta:
        model = RegistroCompleto
        fields = ['nome', 'email', 'telefone', 'cpf', 'data_nascimento', 'nome_mae', 'titulo_eleitor', 'zona', 'secao']
       