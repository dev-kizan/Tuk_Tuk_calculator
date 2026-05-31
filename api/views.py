from rest_framework import viewsets, views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta

from .models import Trip, FuelFillUp
from .serializers import TripSerializer, FuelFillUpSerializer

class TripViewSet(viewsets.ModelViewSet):
    serializer_class = TripSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Drivers can only see their own trips
        return Trip.objects.filter(driver=self.request.user.profile)


class FuelFillUpViewSet(viewsets.ModelViewSet):
    serializer_class = FuelFillUpSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Drivers can only see their own fuel logs
        return FuelFillUp.objects.filter(driver=self.request.user.profile)


class DashboardSummaryView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        driver_profile = request.user.profile
        now = timezone.now()
        
        # Calculate start times for filtering
        start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        start_of_week = start_of_today - timedelta(days=now.weekday()) # Monday
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        periods = {
            'today': start_of_today,
            'week': start_of_week,
            'month': start_of_month
        }

        dashboard_data = {}

        # Query and calculate metrics for each timeframe
        for period_name, start_date in periods.items():
            fares_sum = Trip.objects.filter(
                driver=driver_profile, 
                timestamp__gte=start_date
            ).aggregate(Sum('fare_amount'))['fare_amount__sum'] or 0

            fuel_sum = FuelFillUp.objects.filter(
                driver=driver_profile, 
                timestamp__gte=start_date
            ).aggregate(Sum('cost'))['cost__sum'] or 0

            dashboard_data[period_name] = {
                'total_fares': float(fares_sum),
                'total_fuel': float(fuel_sum),
                'net_earnings': float(fares_sum - fuel_sum),
                'currency': driver_profile.currency
            }

        return Response(dashboard_data, status=status.HTTP_OK)