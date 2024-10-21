from django.urls import path
from shop import views

app_name = 'shop'

urlpatterns = [
    path('', views.ProductListView.as_view(), name='products'),
    path('<slug:slug>', views.product_detail, name='product_detail'),
]


