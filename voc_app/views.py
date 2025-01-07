import uuid
import qrcode
from django.utils.timezone import now
from datetime import timedelta
from django.core.files.base import ContentFile
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView
from django.views import View
from .models import Work

# --- QRコード発行ページ --- #
class PublishView(View):
  def get(self, request):
    return render(request, "survey/publish.html")

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
      work_start_date=work_start_date,
      url_token=url_token,
      url_token_expiry=url_token_expiry,
    )

    # QRコード生成
    survey_url = request.build_absolute_uri(reverse('survey', args=[url_token]))
    qr_image = qrcode.make(survey_url)
    qr_buffer = ContentFile((b""))
    qr_image.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)

    # QRコードをテンプレートで表示
    return render(request, "survey/qr.html", {"qr_code": qr_buffer, "survey_url": survey_url})

# --- QRコードページ --- #
class QrView(TemplateView):
  template_name = "survey/qr.html"

# --- アンケートページ --- #
class SurveyView(TemplateView):
  template_name = "survey/survey.html"

# --- アンケート送信完了ページ --- #
class CompleteView(TemplateView):
  template_name = "survey/complete.html"
