from django.urls import path
from . import views

urlpatterns = [
  # --- 従業員共通
  path('', views.LoginView.as_view(), name='employee'),
  path('logout/', views.LogoutView.as_view(), name='logout'),
  # --- 一般ユーザー
  path('general/', views.GeneralView.as_view(), name='general'),
  path('update/', views.UpdateView.as_view(), name='update'),
  # --- 管理者
  path('admin/', views.AdminView.as_view(), name='admin'),
  # path('voices/', views.VoicesView.as_view(), name='voices'),
  path('voices/', views.SurveyView.as_view(), name='voices'),
  path('awards/', views.AwardsView.as_view(), name='awards'),
  # path('employees/', views.EmployeesView.as_view(), name='employees'),
  path('employees/', views.EmployeesListView.as_view(), name='employees'),
  path('employees/new/', views.EmployeesCreateView.as_view(), name='employees_new'),
  path('employees/edit/<int:pk>', views.EmployeesUpdateView.as_view(), name='employees_edit'),
  path('detail/', views.DetailView.as_view(), name='detail'),
  # --- CSVファイル取得
  path('upload-employee-csv/', views.upload_employee_csv, name='upload_employee_csv'),
  path('upload-work-csv/', views.upload_work_csv, name='upload_work_csv'),
]