from django.urls import path
from . import views

urlpatterns = [
  # --- QRコード発行
  path('', views.PublishView.as_view(), name='publish'),
  # --- アンケート
  path('survey/start/<str:token>', views.StartSurveyView.as_view(), name='start_survey'),
  path('survey/form/', views.SurveyFormView.as_view(), name='survey_form'),
  path('survey/complete/', views.CompleteView.as_view(), name='survey_complete'),
]