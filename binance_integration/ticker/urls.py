from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TickerDataViewSet

router = DefaultRouter()
router.register(r'ticker-data', TickerDataViewSet)

urlpatterns = [
    path('', include(router.urls)),
]