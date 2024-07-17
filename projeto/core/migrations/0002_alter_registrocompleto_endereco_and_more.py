# Generated by Django 5.0.7 on 2024-07-15 04:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registrocompleto',
            name='endereco',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registros_completos', to='core.endereco'),
        ),
        migrations.AlterField(
            model_name='registrosimples',
            name='endereco',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registros_simples', to='core.endereco'),
        ),
    ]
