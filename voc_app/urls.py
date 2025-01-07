from django.urls import path
from . import views

urlpatterns = [
  # --- QRコード発行
  path('', views.PublishView.as_view(), name='publish'),
  path('qr/', views.QrView.as_view(), name='qr'),
  # --- アンケート
  path('survey/', views.SurveyView.as_view(), name='survey'),
  path('complete/', views.CompleteView.as_view(), name='complete'),
]