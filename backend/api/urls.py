from django.urls import path
from . import views

urlpatterns = [
    path('analyze-channels/', views.YouTubeAnalyzerAPIView.as_view(), name='analyze-channels'),
    path('quota-status/', views.QuotaStatusAPIView.as_view(), name='quota-status'),
    path('search-channels/', views.ChannelSearchAPIView.as_view(), name='search-channels'),
    path('analyze-instagram/', views.InstagramAnalyzerAPIView.as_view(), name='analyze-instagram'),
    path('search-instagram/', views.InstagramPageSearchAPIView.as_view(), name='search-instagram'),
]

