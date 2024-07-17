# Generated by Django 5.0.7 on 2024-07-15 03:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Endereco',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cep', models.CharField(max_length=9)),
                ('rua', models.CharField(max_length=255)),
                ('numero', models.CharField(max_length=10)),
                ('bairro', models.CharField(max_length=255)),
                ('cidade', models.CharField(max_length=255)),
                ('estado', models.CharField(max_length=2)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RegistroCompleto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('telefone', models.CharField(max_length=15)),
                ('cpf', models.CharField(max_length=11)),
                ('data_nascimento', models.DateField()),
                ('nome_mae', models.CharField(max_length=255)),
                ('titulo_eleitor', models.CharField(max_length=15)),
                ('zona', models.IntegerField()),
                ('secao', models.IntegerField()),
                ('endereco', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.endereco')),
            ],
        ),
        migrations.CreateModel(
            name='RegistroSimples',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('telefone', models.CharField(max_length=15)),
                ('cpf', models.CharField(max_length=11)),
                ('data_nascimento', models.DateField()),
                ('endereco', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.endereco')),
            ],
        ),
    ]