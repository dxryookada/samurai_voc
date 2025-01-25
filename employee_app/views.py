import csv
from django.http import JsonResponse
from django.utils.timezone import now
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.views import View
from django.views.generic import TemplateView
from django.urls import reverse_lazy, reverse
from django.db import transaction
from django.db.models import Avg, Sum, F
from django.db.models.functions import TruncMonth
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from .models import CustomUser, ConstructionWorker, WorkArea, AwardCount
from voc_app.models import Survey, SurveyResponse, AgeGroup, Work, Question

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
    
# --- データ提供用（棒グラフ）API --- #
"""
月別アンケート平均データを取得する共通関数

employee: 対象の従業員 (Noneの場合は全体データ)
filters: 追加のフィルタ条件 (辞書形式)
return: 質問ごとの月別平均データ
"""
def get_monthly_survey_data(employee=None, filters=None):
    # 初期フィルタ
    survey_filter = {}
    if employee:
        # 特定従業員の工事をフィルタ
        works = ConstructionWorker.objects.filter(employee=employee).values_list('construction_id', flat=True)
        survey_filter['work_id__in'] = works
    
    # 追加フィルタをマージ
    if filters:
        survey_filter.update(filters)

    # すべての質問を取得
    questions = Question.objects.all().order_by('order')
    
    # 質問ごとに月別平均スコアを集計
    question_data = []
    for question in questions:
        monthly_data = (
            SurveyResponse.objects.filter(
                survey__in=Survey.objects.filter(**survey_filter),  # 対象のアンケート
                question=question,
            )
            .annotate(month=TruncMonth('survey__submitted_at'))
            .values('month')
            .annotate(
                average_score=Avg('choice__points')
            )
            .order_by('month')
        )

        data = {
            'question': question.content,
            'months': [item['month'].strftime('%Y-%m') for item in monthly_data if item['month']],
            'average_scores': [item['average_score'] if item['average_score'] is not None else 0 for item in monthly_data],
        }
        question_data.append(data)

    # 自由記入欄AI評価の平均データを取得
    ai_rating_data = (
        Survey.objects.filter(**survey_filter)
        .annotate(month=TruncMonth('submitted_at'))
        .values('month')
        .annotate(
            average_ai_rating=Avg('free_text_ai_rating')
        )
        .order_by('month')
    )

    # 自由記入欄AI評価データを整理
    ai_rating_summary = {
        'question': '自由記入欄AI評価',
        'months': [item['month'].strftime('%Y-%m') for item in ai_rating_data if item['month']],
        'average_scores': [item['average_ai_rating'] if item['average_ai_rating'] is not None else 0 for item in ai_rating_data],
    }

    # 質問データに自由記入欄AI評価を追加
    question_data.append(ai_rating_summary)  

    return question_data

# ログイン中の従業員棒グラフ表示
class SurveyDataView(View):
    def get(self, request, *args, **kwargs):
        # ログイン中の従業員を取得
        user = request.user

        # 年代フィルタを取得
        age_group = request.GET.get('age_group')
        if age_group and age_group != 'all':
            filters = {'age_group_id': age_group}
        else:
            filters = {}  # フィルタなし（すべての年代を対象とする）

        # アンケートデータを取得
        question_data = get_monthly_survey_data(employee=user, filters=filters)

        return JsonResponse({'questions': question_data})
'''
class SurveyDataView(View):
    def get(self, request, *args, **kwargs):
        # ログイン中の従業員を取得
        user = request.user

        # ログイン中の従業員が担当した工事を取得
        works = ConstructionWorker.objects.filter(employee=user).values_list('construction_id', flat=True)

        # 年代フィルタを適用（指定されていない場合は全体データ）
        age_group = request.GET.get('age_group')
        survey_filter = {'work_id__in': works}
        if age_group:
            survey_filter['age_group_id'] = age_group

        # すべての質問を取得
        questions = Question.objects.all().order_by('order')

        # 質問ごと、月ごとに平均ポイントを集計
        question_data = []
        for question in questions:
            monthly_data = (
                SurveyResponse.objects.filter(
                    survey__in=Survey.objects.filter(**survey_filter),  # 担当した工事に関連するアンケート
                    question=question,
                )
                .annotate(month=TruncMonth('survey__submitted_at'))  # アンケート投稿日を月単位で集計
                .values('month')
                .annotate(
                    average_score=Avg('choice__points')  # 選択肢ポイントの平均値
                )
                .order_by('month')
            )

            # 各月のデータを整理
            data = {
                'question': question.content,
                'months': [item['month'].strftime('%Y-%m') for item in monthly_data if item['month']],
                'average_scores': [item['average_score'] if item['average_score'] is not None else 0 for item in monthly_data],
            }
            question_data.append(data)

        # 自由記入欄AI評価の平均データを取得
        ai_rating_data = (
            Survey.objects.filter(**survey_filter)
            .annotate(month=TruncMonth('submitted_at'))
            .values('month')
            .annotate(
                average_ai_rating=Avg('free_text_ai_rating')
            )
            .order_by('month')
        )

        # 自由記入欄AI評価データを整理
        ai_rating_summary = {
            'question': '自由記入欄AI評価',
            'months': [item['month'].strftime('%Y-%m') for item in ai_rating_data if item['month']],
            'average_scores': [item['average_ai_rating'] if item['average_ai_rating'] is not None else 0 for item in ai_rating_data],
        }

        # 質問データに自由記入欄AI評価を追加
        question_data.append(ai_rating_summary)
            
        return JsonResponse({'questions': question_data})
'''

# --- 一般従業員ページ（トップ） --- #
class GeneralView(LoginRequiredMixin, TemplateView):
    template_name = "general/general.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ユーザー情報
        user = self.request.user

        # 対象年月
        year = int(self.request.GET.get('year', now().year))
        years = [year - 2, year - 1, year]
        month = int(self.request.GET.get('month', now().month))
        months = list(range(1, 13))

        # ログインユーザーの表彰回数 
        award_counts = {
            'gold': AwardCount.objects.filter(employee=user, award_type__name='金').count(),
            'silver': AwardCount.objects.filter(employee=user, award_type__name='銀').count(),
            'copper': AwardCount.objects.filter(employee=user, award_type__name='銅').count(),
        }

        # 年代
        age_groups = AgeGroup.objects.all()

        # --- AIアドバイス ここから --- #
        # Hugging Faceモデルを準備（日本語対応の生成モデル）
        model_name = "cyberagent/open-calm-small"

        # 適切なトークナイザを明示的に指定
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name)

        # パイプラインの設定
        generator = pipeline("text-generation", model=model, tokenizer=tokenizer)

        # ユーザーに関連するアンケートを取得
        surveys = Survey.objects.filter(
            work__constructionworker__employee=user,  # リレーションを辿って従業員に関連付け
            submitted_at__year=year
        ).distinct()  # 重複排除

        # 一度生成したアドバイスをキャッシュに保存
        cache_key = f"advice_user_{user}"
        advice_list = cache.get(cache_key)

        # キャッシュがない場合アンケート自由記入欄から具体的なアドバイスを生成
        if not advice_list:
            advice_list = []
            for survey in surveys:
                if survey.free_text:
                    # 生成のプロンプトを定義
                    prompt = (
                        f"以下の自由記入欄の内容を基に、従業員に向けた具体的なアドバイスを作成してください。\n"
                        f"自由記入欄: 「{survey.free_text}」\n"
                        f"アドバイス: \n"
                    )
                    # AIモデルでアドバイス文を生成
                    generated_text = generator(prompt, max_length=150, num_return_sequences=3, do_sample=True, temperature=0.7)
                    advice = generated_text[0]['generated_text'].replace(prompt, "").strip()
                    advice_list.append(advice)
        # --- AIアドバイス ここまで --- #

        # --- 月別アンケートTOP3 ここから --- #
        # 重み付きスコアを計算
        top_employees = (
            ConstructionWorker.objects.values(
                'employee_id',  # 従業員ID
                'employee__name'  # 従業員名
            )
            .annotate(
                weighted_question_score=Sum(
                    F('construction__survey__surveyresponse__choice__points') *
                    F('construction__survey__surveyresponse__question__weight')  # 質問スコア × 重み
                ),
                weighted_free_text_score=Sum(
                    F('construction__survey__free_text_ai_rating') * 2.0  # 自由記入欄AI評価 × 重み(2.0)
                ),
                total_weighted_score=(
                    F('weighted_question_score') + F('weighted_free_text_score')
                )
            )
            .order_by('-total_weighted_score')[:3]  # Top3を取得
        )

        # Top3データ整形
        top3_employees_data = [
            {
                'employee_id': employee['employee_id'],
                'name': employee['employee__name'],
            }
            for employee in top_employees
        ]

        # 1位の従業員の月別アンケートデータ取得
        if top3_employees_data:
            top_employee = top3_employees_data[0]
            monthly_data = get_monthly_survey_data(employee=top_employee['employee_id'])

            # コンテキストに1位のデータと棒グラフ用データを追加
            context.update({
                'top_employee_name': top_employee['name'],
                'monthly_data': monthly_data,
            })

        # FetchAPIからのアクセスか、通常のアクセスかどうか
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # アンケートデータを取得（get_monthly_survey_data自作関数再利用）
            question_data = get_monthly_survey_data(employee=top_employee['employee_id'])

            return JsonResponse({'questions': question_data})
        else:
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
                'advice_list': advice_list,  # 生成された具体的なAIアドバイス文リスト
                'top3_employees_data': top3_employees_data,
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