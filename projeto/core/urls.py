from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('registro-simples/', views.registro_simples, name='registro_simples'),
    path('registro-completo/', views.registro_completo, name='registro_completo'),
    path('visualizar_registros_simples/', views.visualizar_registros_simples, name='visualizar_registros_simples'),
    path('visualizar_registros_completos/', views.visualizar_registros_completos, name='visualizar_registros_completos'),
    path('editar_registro_simples/<int:pk>/', views.editar_registro_simples, name='editar_registro_simples'),
    path('editar_registro_completo/<int:pk>/', views.editar_registro_completo, name='editar_registro_completo'),
    path('excluir_registro_simples/<int:pk>/', views.excluir_registro_simples, name='excluir_registro_simples'),
    path('excluir_registro_completo/<int:pk>/', views.excluir_registro_completo, name='excluir_registro_completo'),
    path("preenche_formulario/", views.preenche_formulario, name="preenche_formulario"),
    path("visualizar_mapa/", views.visualizar_mapa, name="visualizar_mapa"),
    path('atualizar_endereco/', views.atualizar_endereco, name='atualizar_endereco'),
    path('salvar_novo_endereco/', views.salvar_novo_endereco, name='salvar_novo_endereco'),
    
]
