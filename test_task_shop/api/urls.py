from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CompleteOrderAPIView
from django.urls import path, include

router = DefaultRouter()
router.register(r'products', ProductViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('chekout/', CompleteOrderAPIView.as_view()),
]