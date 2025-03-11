from rest_framework import viewsets
from ticker.models import TickerData
from ticker.serializers import TickerDataSerializer

class TickerDataViewSet(viewsets.ModelViewSet):
    queryset = TickerData.objects.all()
    serializer_class = TickerDataSerializer
    filterset_fields = ['symbol']