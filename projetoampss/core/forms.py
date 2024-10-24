from django import forms
from .models import RegistroSimples, RegistroCompleto, Endereco, CustomUser
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('is_admin',)

class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')
        
        
class EnderecoForm(forms.ModelForm):
    class Meta:
        model = Endereco
        fields = ['cep', 'rua', 'numero', 'bairro', 'cidade', 'estado']


class RegistroSimplesForm(forms.ModelForm):
    class Meta:
        model = RegistroSimples
        fields = ['nome', 'email', 'telefone', 'cpf', 'data_nascimento']
       
class RegistroCompletoForm(forms.ModelForm):
    data_nascimento = forms.DateField(
        widget=forms.DateInput(format='%d/%m/%Y', attrs={'class': 'datepicker', 'placeholder': 'dd/mm/yyyy'}),
        input_formats=['%d/%m/%Y']
    )

    class Meta:
        model = RegistroCompleto
        fields = ['nome', 'email', 'telefone', 'cpf', 'data_nascimento', 'nome_mae', 'titulo_eleitor', 'zona_secao', 'municipio', 'endereco_votacao', 'local']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['zona_secao'].required = False  # Novo campo combinado
        self.fields['municipio'].required = False
        self.fields['endereco_votacao'].required = False 
        self.fields['local'].required = False
    