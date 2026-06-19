import os
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import viewsets, views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta
from django.shortcuts import render
from api.authentication import SupabaseJWTAuthentication

from .models import Trip, FuelFillUp
from .serializers import TripSerializer, FuelFillUpSerializer

def home(request):
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_anon_key = os.environ.get("SUPABASE_ANON_KEY")
    
    print(f"DEBUG SUPABASE_URL: {supabase_url}") 
    
    context = {
        'SUPABASE_URL': supabase_url or "MISSING_URL",
        'SUPABASE_ANON_KEY': supabase_anon_key or "MISSING_KEY",
    }

    return render(request, 'home.html', context)

def login(request):
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_anon_key = os.environ.get("SUPABASE_ANON_KEY")
    
    context = {
        'SUPABASE_URL': supabase_url or "MISSING_URL",
        'SUPABASE_ANON_KEY': supabase_anon_key or "MISSING_KEY",
    }
    return render(request, 'login.html', context)

@api_view(['GET'])
@permission_classes([AllowAny])
def dashboard_view(request):
    return render(request, 'dashboard.html')

class TripViewSet(viewsets.ModelViewSet):
    serializer_class = TripSerializer
    authentication_classes = [SupabaseJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Trip.objects.filter(driver=self.request.user.profile)
    
    def perform_create(self, serializer):
        serializer.save(driver=self.request.user.profile)


class FuelFillUpViewSet(viewsets.ModelViewSet):
    serializer_class = FuelFillUpSerializer
    authentication_classes = [SupabaseJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FuelFillUp.objects.filter(driver=self.request.user.profile)
    
    def perform_create(self, serializer):
        serializer.save(driver=self.request.user.profile)


class DashboardSummaryView(views.APIView):
    authentication_classes = [SupabaseJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        
        try:
            driver_profile = user.profile
        except ObjectDoesNotExist:
            from .models import Profile 
            driver_profile = Profile.objects.create(user=user, currency="LKR")

        now = timezone.now()
        start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        start_of_week = start_of_today - timedelta(days=now.weekday())
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        periods = {
            'today': start_of_today,
            'week': start_of_week,
            'month': start_of_month
        }

        dashboard_data = {}

        for period_name, start_date in periods.items():
            trips_queryset = Trip.objects.filter(
                driver=driver_profile, 
                timestamp__gte=start_date
            ).order_by('-timestamp')

            fuel_queryset = FuelFillUp.objects.filter(
                driver=driver_profile, 
                timestamp__gte=start_date
            ).order_by('-timestamp')

            fares_sum = trips_queryset.aggregate(Sum('fare_amount'))['fare_amount__sum'] or 0
            fuel_sum = fuel_queryset.aggregate(Sum('cost'))['cost__sum'] or 0

            individual_logs = []

            for trip in trips_queryset:
                individual_logs.append({
                    'id': f"trip_{trip.id}",
                    'type': 'fare',
                    'amount': float(trip.fare_amount),
                    'description': trip.notes or "Passenger Fare",
                    'timestamp': trip.timestamp.isoformat()
                })

            for fuel in fuel_queryset:
                individual_logs.append({
                    'id': f"fuel_{fuel.id}",
                    'type': 'fuel',
                    'amount': float(fuel.cost),
                    'description': f"Fuel Refill ({fuel.liters}L)" if fuel.liters else "Fuel Refill",
                    'timestamp': fuel.timestamp.isoformat()
                })

            individual_logs.sort(key=lambda x: x['timestamp'], reverse=True)

            dashboard_data[period_name] = {
                'total_fares': float(fares_sum),
                'total_fuel': float(fuel_sum),
                'net_earnings': float(fares_sum - fuel_sum),
                'currency': driver_profile.currency,
                'logs': individual_logs
            }

        return Response(dashboard_data, status=status.HTTP_200_OK)