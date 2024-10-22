from django.urls import path

from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_view, name='cart_view'),
    path('add/', views.cart_add, name='add_to_cart'),
    path('delete/', views.delete_product, name='delete_to_cart'),
    path('update/', views.cart_update, name='update_to_cart')

]


