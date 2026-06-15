from rest_framework import serializers
from .models import Trip, FuelFillUp, Profile

class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ['id', 'driver', 'fare_amount', 'timestamp', 'notes']
        read_only_fields = ['driver']
        
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['driver'] = user.profile
        return super().create(validated_data)


class FuelFillUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = FuelFillUp
        fields = ['id', 'driver', 'cost', 'liters', 'timestamp']
        read_only_fields = ['driver']

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