from django.shortcuts import render
from django.views.generic import TemplateView

# --- ログインページ
class LoginView(TemplateView):
  template_name = "login.html"

# --- 一般従業員ページ（トップ）
class GeneralView(TemplateView):
  template_name = "general/general.html"

# --- 一般従業員ページ（データ更新）
class UpdateView(TemplateView):
  template_name = "general/update.html"

# --- 管理者ページ（トップ）
class AdminView(TemplateView):
  template_name = "admin/admin.html"

# --- お客様の声一覧ページ（管理者）
class VoicesView(TemplateView):
  template_name = "admin/voices.html"

# --- 表彰状贈呈一覧ページ（管理者）
class AwardsView(TemplateView):
  template_name = "admin/awards.html"

# --- 従業員一覧ページ（管理者）
class EmployeesView(TemplateView):
  template_name = "admin/employees.html"

# --- 従業員詳細ページ（管理者）
class DetailView(TemplateView):
  template_name = "admin/detail.html"