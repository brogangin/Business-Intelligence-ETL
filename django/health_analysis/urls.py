from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('prediction/', views.diabetes_prediction_view, name='diabetes_prediction'),
    path('segmentation/', views.population_segmentation_view, name='population_segmentation'),
    path('risk-factors/', views.high_bp_risk_factors_view, name='highbp_risk_factors'),
]