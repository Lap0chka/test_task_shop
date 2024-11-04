from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CompleteOrderAPIView, ProductViewSet

router = DefaultRouter()
router.register(r"products", ProductViewSet)


urlpatterns = [
    path("", include(router.urls)),
    path("checkout/", CompleteOrderAPIView.as_view()),
]
