from django.db import models
from .utils import get_lat_lon_from_address
from django.contrib.auth.models import AbstractUser, Group, Permission

class CustomUser(AbstractUser):
    is_admin = models.BooleanField(default=False)
    def __str__(self):
        return self.username

class Endereco(models.Model):
    endereco = models.CharField(max_length=255, default='Endereço padrão')
    cep = models.CharField(max_length=9)
    rua = models.CharField(max_length=255)
    numero = models.CharField(max_length=10)
    bairro = models.CharField(max_length=255)
    cidade = models.CharField(max_length=255)
    estado = models.CharField(max_length=2)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    endereco_formatado = models.CharField(max_length=255, default='Endereço não formatado')

    def __str__(self):
        return self.endereco
    
    def save(self, *args, **kwargs):
        self.endereco_formatado = f"{self.rua}, {self.numero}, {self.bairro}, {self.cidade}, {self.estado}"
        super(Endereco, self).save(*args, **kwargs)

    def __str__(self):
        return self.endereco_formatado or f"{self.rua}, {self.numero}, {self.bairro}, {self.cidade}, {self.estado}"

class RegistroSimples(models.Model):
    nome = models.CharField(max_length=255)
    email = models.EmailField()
    telefone = models.CharField(max_length=15)
    cpf = models.CharField(max_length=11)
    data_nascimento = models.DateField()
    endereco = models.ForeignKey(Endereco, related_name='registros_simples', on_delete=models.CASCADE)

    def __str__(self):
        return self.nome

class RegistroCompleto(models.Model):
    nome = models.CharField(max_length=255)
    email = models.EmailField()
    telefone = models.CharField(max_length=15)
    cpf = models.CharField(max_length=11)
    data_nascimento = models.CharField(max_length=10)
    nome_mae = models.CharField(max_length=255, blank=True, null=True)
    titulo_eleitor = models.CharField(max_length=25, blank=True, null=True)
    zona_secao = models.CharField(max_length=30, blank=True, null=True)
    municipio = models.CharField(max_length=255, blank=True, null=True)
    local = models.CharField(max_length=255, blank=True, null=True)
    endereco_votacao = models.CharField(max_length=255, blank=True, null=True)
    endereco = models.ForeignKey(Endereco, related_name='registros_completos', on_delete=models.CASCADE)

    def __str__(self):
        return self.nome
    
    def save(self, *args, **kwargs):
        if not self.endereco.latitude or not self.endereco.longitude:
            full_address = f"{self.endereco.endereco_formatado}, {self.municipio}"
            lat, lon = get_lat_lon_from_address(full_address)
            if lat and lon:
                self.endereco.latitude = lat
                self.endereco.longitude = lon
                self.endereco.save()

        super(RegistroCompleto, self).save(*args, **kwargs)
