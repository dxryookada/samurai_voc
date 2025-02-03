import uuid
import qrcode
import base64
from django.utils.timezone import now
from datetime import timedelta
from django.core.files.base import ContentFile
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from django.views import View
from .models import Work, Survey, SurveyResponse, Question, Choice
from .forms import SurveyForm
from .ai_utils import analyze_free_text  # TextBlob分析用の関数

# --- QRコード発行ページ --- #
class PublishView(View):
    # GETメソッド
    def get(self, request):
        return render(request, "survey/publish.html")

    # POSTメソッド
    def post(self, request):
        # フォームデータ取得
        receipt_number = request.POST.get("receipt-number")
        receipt_date = request.POST.get("receipt-date")
        work_start_date = request.POST.get("work-day")

        # 入力データのバリデーション
        if not receipt_number or not receipt_date or not work_start_date:
            return render(request, "survey/publish.html", {"error": "すべてのフィールドを入力してください。"})
    
        # URLトークン生成と期限設定
        url_token = str(uuid.uuid4())
        url_token_expiry = now().date() + timedelta(days=7)  # 7日間有効

        # 工事テーブルに保存
        work = Work.objects.create(
            receipt_number=receipt_number,
            receipt_date=receipt_date,
            url_token=url_token,
            url_token_expiry=url_token_expiry,
        )

        # QRコード生成
        survey_url = request.build_absolute_uri(reverse('start_survey', args=[url_token]))
        qr_image = qrcode.make(survey_url)
        qr_buffer = ContentFile((b""))
        qr_image.save(qr_buffer, format="PNG")
        qr_buffer.seek(0)

        # QRコード画像をBase64エンコード
        qr_code_base64 = base64.b64encode(qr_buffer.read()).decode('utf-8')

        # QRコードをテンプレートで表示
        return render(request, "survey/qr.html", {"qr_code": qr_code_base64, "survey_url": survey_url})

# --- URLトークンチェック --- #
class StartSurveyView(View):
    def get(self, request, token):
        work = get_object_or_404(Work, url_token=token)

        # トークンの有効期限チェック
        if work.url_token_expiry < now().date():
            return HttpResponseForbidden("このURLトークンは期限切れです。")
    
        # 工事IDをセッションに保存
        request.session['work_id'] = work.id

        # アンケートフォームにリダイレクト
        return redirect('survey_form')

# --- アンケートページ --- #
class SurveyFormView(FormView):
    template_name = "survey/survey.html"
    form_class = SurveyForm
    success_url = reverse_lazy('survey_complete')

    def form_valid(self, form):
        # セッションから工事IDを取得
        work_id = self.request.session.get('work_id')
        if not work_id:
            return HttpResponseForbidden("有効な工事IDがありません。")
        
        # Workインスタンスを取得
        work = get_object_or_404(Work, id=work_id)

        # Surveyモデルに保存
        survey = Survey.objects.create(
            work = work,
            gender = form.cleaned_data['gender'],
            age_group = form.cleaned_data['age_group'],
            free_text = form.cleaned_data.get('free_text', None),
            free_text_ai_rating = analyze_free_text(form.cleaned_data.get('free_text', None)),
        )

        # 各質問の回答をSurveyResponseモデルに保存
        for field_name, value in form.cleaned_data.items():
            if field_name.startswith('question'):  # フィールド名が"question"で始まる場合
                try:
                    # 質問と選択肢の対応を取得
                    question_order = int(field_name.replace('question', ''))
                    question = Question.objects.get(order=question_order)
                    choice = Choice.objects.get(id=value.id)  # 選択肢を取得

                    # SurveyResponseモデルに保存
                    SurveyResponse.objects.create(
                        survey=survey,
                        question=question,
                        choice=choice,
                    )
                except (Question.DoesNotExist, Choice.DoesNotExist, ValueError):
                    return HttpResponseForbidden("無効なデータが含まれています。")
                
        # 正常終了時のみセッションを削除
        del self.request.session['work_id']

        return super().form_valid(form)

# --- アンケート送信完了ページ --- #
class CompleteView(TemplateView):
    template_name = "survey/complete.html"
