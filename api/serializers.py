from rest_framework import serializers
from .models import Trip, FuelFillUp, Profile

class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ['id', 'fare_amount', 'timestamp', 'notes']
        
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['driver'] = user.profile
        return super().create(validated_data)


class FuelFillUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = FuelFillUp
        fields = ['id', 'cost', 'liters', 'timestamp']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['driver'] = user.profile
        return super().create(validated_data)


class DashboardSummarySerializer(serializers.Serializer):
    period = serializers.CharField()
    total_fares = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_fuel = serializers.DecimalField(max_digits=10, decimal_places=2)
    net_earnings = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField()