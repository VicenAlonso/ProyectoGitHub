from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    # uRL para la página de inicio
    path('home/', views.home, name='home'),
    path('login/', views.custom_login, name='custom_login'),
     # URL  de orden de compra
    path('order/', views.order, name='order'), 
    path('submit_order/', views.submit_order, name='submit_order'),  # Nueva URL para enviar la orden
    path('download_order_pdf/<int:order_id>/', views.download_order_pdf, name='download_order_pdf'),
]
