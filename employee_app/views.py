from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import AwardCount

# --- コンテキスト
class BaseContext:
    def get_context_data(self, **kwargs):
        # テンプレートファイルにparamsデータを渡す
        context = super().get_context_data(**kwargs)
        params = {
            'title': '機械学習 | Django基礎',
            'header': self.header,
            'current_path': self.request.path, # パスの取得
            'val': self.val, # 通常の出力
            'pre': self.pre, # <pre>で出力
            'url': self.url, # 画像出力
        }
        context.update(params)
        return context

# --- ログインページ
class LoginView(LoginView):
  template_name = "login.html"
  redirect_authenticated_user = True 

  def get_success_url(self):
    if self.request.user.is_staff:
      return reverse_lazy('admin')
    return reverse_lazy('general')
  
# --- ログアウト動作
class logoutView(LogoutView):
  def dispatch(self, request, *args, **kwargs):
    messages.success(request, "ログアウトしました")
    response = super().dispatch(request, *args, **kwargs)  # 親クラスの処理を呼び出す
    return response

# --- 一般従業員ページ（トップ）
class GeneralView(LoginRequiredMixin, TemplateView):
    template_name = "general/general.html"

    # コンテキスト
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        award_counts = {
            'gold': AwardCount.objects.filter(employee=user, award_type__name='金').count(),
            'silver': AwardCount.objects.filter(employee=user, award_type__name='銀').count(),
            'copper': AwardCount.objects.filter(employee=user, award_type__name='銅').count(),
        }
        context.update({
            'user_name': user.name,
            'advice': user.advice,
            'award_counts': award_counts,
        })
        return context

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