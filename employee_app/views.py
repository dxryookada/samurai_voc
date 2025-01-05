from django.utils.timezone import now
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import TemplateView
from django.urls import reverse_lazy, reverse
from .models import CustomUser, AwardCount
from voc_app.models import AgeGroup

# --- ログインページ --- #
class LoginView(LoginView):
    template_name = "login.html"
    redirect_authenticated_user = True 

    def get_success_url(self):
        if self.request.user.is_staff:
          return reverse_lazy('admin')
        return reverse_lazy('general')
  
# --- ログアウト動作 --- #
class logoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "ログアウトしました")
        response = super().dispatch(request, *args, **kwargs)  # 親クラスの処理を呼び出す
        return response

# --- 一般従業員ページ（トップ） --- #
class GeneralView(LoginRequiredMixin, TemplateView):
    template_name = "general/general.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ユーザー情報
        user = self.request.user

        # 対象年月
        year = self.request.GET.get('year', now().year) 
        years = [int(year) - 2, int(year) - 1, int(year)]
        month = self.request.GET.get('month', now().month)
        months = list(range(1, 13))

        # 表彰 
        award_counts = {
            'gold': AwardCount.objects.filter(employee=user, award_type__name='金').count(),
            'silver': AwardCount.objects.filter(employee=user, award_type__name='銀').count(),
            'copper': AwardCount.objects.filter(employee=user, award_type__name='銅').count(),
        }

        # 年代
        age_groups = AgeGroup.objects.all()

        # コンテキスト
        context.update({
            'user_name': user.name,
            'advice': user.advice,
            'award_counts': award_counts,
            'selected_year': int(year),
            'years': years,
            'selected_month': int(month),
            'months': months,
            'age_groups': age_groups, 
        })
        return context

# --- 一般従業員ページ（マイページ・データ更新） --- #
class UpdateView(LoginRequiredMixin, View):
    template_name = "general/update.html"

    # 初期画面
    def get(self, request, *args, **kwargs):
        user = get_object_or_404(CustomUser, pk=request.user.pk)
        context = {
            'employee_id': user.employee_id,
            'user_name': user.name,
            'work_area': user.work_area,
            'email': user.email,
        }
        return render(request, self.template_name, context)

    # データ更新  
    def post(self, request, *args, **kwargs):
        employee_id = request.POST.get('id')
        user_name = request.POST.get('user_name')
        work_area = request.POST.get('area')
        email = request.POST.get('email')

        user = get_object_or_404(CustomUser, pk=request.user.pk)

        try:
            user.employee_id = employee_id
            user.name = user_name
            user.work_area = work_area
            user.email = email
            user.save()

            messages.success(request, "従業員情報を更新しました")
            return redirect(reverse("general"))
        except Exception as e:
            messages.error(request, "従業員情報の更新に失敗しました")
            return render(request, self.template_name, {
                'employee_id': user.employee_id,
                'user_name': user.name,
                'work_area': user.work_area,
                'email': user.email,
                'error': str(e)
            })

# --- 管理者ページ（トップ） --- #
class AdminView(LoginRequiredMixin, TemplateView):
    template_name = "admin/admin.html"

# --- お客様の声一覧ページ（管理者） --- #
class VoicesView(LoginRequiredMixin, TemplateView):
    template_name = "admin/voices.html"

# --- 表彰状贈呈一覧ページ（管理者） --- #
class AwardsView(LoginRequiredMixin, TemplateView):
    template_name = "admin/awards.html"

# --- 従業員一覧ページ（管理者） --- #
class EmployeesView(LoginRequiredMixin, TemplateView):
    template_name = "admin/employees.html"

# --- 従業員詳細ページ（管理者） --- #
class DetailView(LoginRequiredMixin, TemplateView):
    template_name = "admin/detail.html"