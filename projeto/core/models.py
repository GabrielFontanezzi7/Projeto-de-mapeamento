from django.db import models

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
    data_nascimento = models.DateField()
    nome_mae = models.CharField(max_length=255)
    titulo_eleitor = models.CharField(max_length=15)
    zona = models.IntegerField()
    secao = models.IntegerField()
    endereco = models.ForeignKey(Endereco, related_name='registros_completos', on_delete=models.CASCADE)

    def __str__(self):
        return self.nome
