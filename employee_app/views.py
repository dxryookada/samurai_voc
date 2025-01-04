from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

# --- ログインページ
class LoginView(LoginView):
  template_name = "login.html"
  redirect_authenticated_user = True 

  def get_success_url(self):
    if self.request.user.is_staff:
      return reverse_lazy('admin')
    return reverse_lazy('general')

# --- 一般従業員ページ（トップ）
class GeneralView(LoginRequiredMixin, TemplateView):
  template_name = "general/general.html"

# --- 一般従業員ページ（データ更新）
class UpdateView(LoginRequiredMixin, TemplateView):
  template_name = "general/update.html"

# --- 管理者ページ（トップ）
class AdminView(LoginRequiredMixin, TemplateView):
  template_name = "admin/admin.html"

# --- お客様の声一覧ページ（管理者）
class VoicesView(LoginRequiredMixin, TemplateView):
  template_name = "admin/voices.html"

# --- 表彰状贈呈一覧ページ（管理者）
class AwardsView(LoginRequiredMixin, TemplateView):
  template_name = "admin/awards.html"

# --- 従業員一覧ページ（管理者）
class EmployeesView(LoginRequiredMixin, TemplateView):
  template_name = "admin/employees.html"

# --- 従業員詳細ページ（管理者）
class DetailView(LoginRequiredMixin, TemplateView):
  template_name = "admin/detail.html"