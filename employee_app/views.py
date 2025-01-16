import csv
from django.utils.timezone import now
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import TemplateView
from django.urls import reverse_lazy, reverse
from django.db import transaction
from .models import CustomUser, ConstructionWorker, WorkArea, AwardCount
from voc_app.models import SurveyResponse, AgeGroup, Work

# --- ログインページ --- #
class LoginView(LoginView):
    template_name = "login.html"
    redirect_authenticated_user = True 

    def get_success_url(self):
        if self.request.user.is_staff:
            return reverse_lazy('admin')
        return reverse_lazy('general')

# --- ログアウト動作(POSTメソッドのみ可能) --- #
class LogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "ログアウトしました")
        response = super().dispatch(request, *args, **kwargs)  # 親クラスの処理を呼び出す
        return response
    
# --- データ提供用API --- #


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

    # 初期画面（GETメソッド）
    def get(self, request, *args, **kwargs):
        user = get_object_or_404(CustomUser, pk=request.user.pk)
        context = {
            'employee_id': user.employee_id,
            'user_name': user.name,
            'work_area': user.work_area,
            'email': user.email,
        }
        return render(request, self.template_name, context)

    # データ更新（POSTメソッド）
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

# --- 従業員CSV取得（管理者） --- #
def upload_employee_csv(request):
    if request.method == "POST":
        # ファイル読み取り
        csv_file = request.FILES['employee_csv']
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file, delimiter=',')
        for row in reader:
            # フィールドをマッピング
            work_area, _ = WorkArea.objects
            CustomUser.objects.update_or_create(
                employee_id=row['従業員ID'],
                defaults={
                    'work_area': work_area,
                    'name': row['従業員'],
                    'email': row['携帯メールアドレス'],
                }
            )
        return redirect('success')
    return render(request, 'admin.html')

# --- 工事情報CSV取得（管理者） --- #
def upload_work_csv(request):
    if request.method == "POST" and request.FILES.get('work_csv'):
        # ファイル読み取り
        csv_file = request.FILES['work_csv']
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file, delimiter=',')

        try:
            # データ整合性を保つためにトランザクションを使用
            with transaction.atomic():
                for row in render:
                    # 工事テーブルから受付番号を元に取得
                    work = Work.objects.filter(
                        receipt_number=row['受付番号'],
                        receipt_date=row['受付日時']
                    ).first()

                    if not work:
                        # 工事情報が見つからない場合はスキップまたはエラー処理
                        print(f"受付番号 {row['受付番号']} の工事情報が見つかりません")
                        continue

                    # 要員１の従業員情報を取得
                    employee_1 = CustomUser.objects.filter(employee_id=row['要員ＩＤ１']).first()
                    if employee_1:
                        ConstructionWorker.objects.update_or_create(
                            construction=work,
                            employee=employee_1,
                        )
                    else:
                        print(f"要員ＩＤ１ {row['要員ＩＤ１']} に該当する従業員が見つかりません")

                    # 要員２の従業員情報を取得
                    employee_2 = CustomUser.objects.filter(employee_id=row['要員ＩＤ２']).first()
                    if employee_2:
                        ConstructionWorker.objects.update_or_create(
                            construction=work,
                            employee=employee_2,
                        )
                    else:
                        print(f"要員ＩＤ２ {row['要員ＩＤ２']} に該当する従業員が見つかりません")
            return redirect('success')
        except Exception as e:
            print(f"エラーが発生しました: {str(e)}")
            return render(request, 'admin.html', {'error': 'エラーが発生しました。CSVファイルを確認してください。'})
    return render(request, 'admin.html')

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