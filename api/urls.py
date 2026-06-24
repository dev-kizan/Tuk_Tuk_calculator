from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TripViewSet, FuelFillUpViewSet, DashboardSummaryView, SyncOfflineDataView, dashboard_view, home, login

router = DefaultRouter()
router.register(r'trips', TripViewSet, basename='trip')
router.register(r'fuel', FuelFillUpViewSet, basename='fuel')

urlpatterns = [
    path('', home, name='index'),
    path('home/', home, name='home'),
    path('login/', login, name='login'),
    path('dashboard/', dashboard_view, name='dashboard-page'),

    path('api/', include(router.urls)),

    path('api/dashboard-summary/', DashboardSummaryView.as_view(), name='dashboard-summary'),
    path('api/sync-offline/', SyncOfflineDataView.as_view(), name='sync-offline-data'),
]