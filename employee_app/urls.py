from django.urls import path
from . import views

urlpatterns = [
  path('', views.LoginView.as_view(), name='login'),
  # --- 一般ユーザー
  path('general/', views.GeneralView.as_view(), name='general'),
  path('update/', views.UpdateView.as_view(), name='update'),
  # --- 管理者
  path('admin/', views.AdminView.as_view(), name='admin'),
  path('voices/', views.VoicesView.as_view(), name='voices'),
  path('awards/', views.AwardsView.as_view(), name='awards'),
  path('employees/', views.EmployeesView.as_view(), name='employees'),
  path('detail/', views.DetailView.as_view(), name='detail'),
]