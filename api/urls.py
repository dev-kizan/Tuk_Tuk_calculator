from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TripViewSet, FuelFillUpViewSet, DashboardSummaryView

router = DefaultRouter()
router.register(r'trips', TripViewSet, basename='trip')
router.register(r'fuel', FuelFillUpViewSet, basename='fuel')

urlpatterns = [
    path('', include(router.urls)),
    # GET/POST /api/trips/
    # GET/PUT/DELETE /api/trips/<id>/
    # GET /api/dashboard/
    path('dashboard/', DashboardSummaryView.as_view(), name='dashboard-summary'),
]