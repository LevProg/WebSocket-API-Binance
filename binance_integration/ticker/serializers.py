from rest_framework import serializers
from ticker.models import TickerData

class TickerDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TickerData
        fields = ['id', 'timestamp', 'symbol', 'price', 'volume']