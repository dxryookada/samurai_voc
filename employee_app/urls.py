from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
  # --- 従業員共通
  path('', views.LoginView.as_view(), name='employee'),
  path('logout/', views.LogoutView.as_view(), name='logout'),
  # --- 一般ユーザー
  path('general/', views.GeneralView.as_view(), name='general'),
  path('general/api/survey-data/', views.SurveyDataView.as_view(), name='survey_data'),
  path('update/', views.UpdateView.as_view(), name='update'),
  # --- パスワードリセット
  # パスワードリセットを開始するためのビュー
  path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
  # リセット完了通知
  path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
  # パスワードリセット用リンク（メールからアクセス）
  path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
  # パスワード変更完了後の通知
  path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
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