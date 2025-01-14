from django.db import models
from employee_app.models import WorkArea

# --- 性別テーブル --- #
class Gender(models.Model):
    name = models.CharField(verbose_name="性別", max_length=50, unique=True)

    class Meta:
        verbose_name = '性別'
        verbose_name_plural = '性別一覧'

    def __str__(self):
        return self.name

# --- 年代テーブル --- #
class AgeGroup(models.Model):
    name = models.CharField(verbose_name="年代", max_length=50, unique=True)

    class Meta:
        verbose_name = '年代'
        verbose_name_plural = '年代一覧'

    def __str__(self):
        return self.name
    
# --- 工事テーブル --- #
class Work(models.Model):
    work_area = models.ForeignKey(WorkArea, verbose_name="作業エリア", on_delete=models.CASCADE, null=True)
    receipt_number = models.IntegerField(verbose_name="受付番号")
    receipt_date = models.DateTimeField(verbose_name="受付日")
    url_token = models.CharField(verbose_name="URLトークン", max_length=255, unique=True)
    url_token_expiry = models.DateField(verbose_name="URLトークン期限")

    class Meta:
        verbose_name = '工事情報'
        verbose_name_plural = '工事一覧'
        unique_together = ('receipt_number', 'receipt_date')

    def __str__(self):
        formatted_number = f"{self.receipt_number:06}"
        return f"工事 ID: {self.id} - 受付番号: {formatted_number})"

# --- アンケートテーブル --- #
class Survey(models.Model):
    work = models.ForeignKey(Work, verbose_name="工事ID", on_delete=models.CASCADE)
    gender = models.ForeignKey(Gender, verbose_name="性別", on_delete=models.CASCADE)
    age_group = models.ForeignKey(AgeGroup, verbose_name="年代", on_delete=models.CASCADE)
    free_text = models.TextField(verbose_name="自由記入欄", blank=True, null=True)
    free_text_ai_rating = models.IntegerField(verbose_name="自由記入欄AI評価", blank=True, null=True)
    submitted_at = models.DateField(verbose_name="投稿日", auto_now_add=True)

    class Meta:
        verbose_name = 'アンケート内容'
        verbose_name_plural = 'アンケート一覧'

    def __str__(self):
        return f"アンケート ID: {self.id}"

# --- 質問内容テーブル --- #
class Question(models.Model):
    content = models.TextField(verbose_name="内容")
    weight = models.FloatField(verbose_name="重み", default=1.0)
    order = models.PositiveBigIntegerField(verbose_name="順序")

    class Meta:
        verbose_name = '質問内容'
        verbose_name_plural = '質問内容一覧'
        ordering = ['order']

    def __str__(self):
        return f"質問 ID: {self.id} - {self.content}"
    
# --- 選択肢テーブル --- #
class Choice(models.Model):
    question = models.ForeignKey(Question, verbose_name="質問内容", on_delete=models.CASCADE)
    content = models.CharField(verbose_name="選択肢", max_length=255)
    points = models.IntegerField(verbose_name="ポイント", default=0)
    order = models.PositiveBigIntegerField(verbose_name="順序")

    class Meta:
        verbose_name = '選択肢'
        verbose_name_plural = '選択肢一覧'
        ordering = ['order']

    def __str__(self):
        return self.content
    
# --- アンケート回答テーブル --- #
class SurveyResponse(models.Model):
    survey = models.ForeignKey(Survey, verbose_name="アンケート", on_delete=models.CASCADE)
    question = models.ForeignKey(Question, verbose_name="質問内容", on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, verbose_name="選択肢", on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'アンケート回答'
        verbose_name_plural = 'アンケート回答一覧'
        unique_together = ('survey', 'question')  # 同じアンケート内で同じ質問の回答を1つに制限

    def __str__(self):
        return f"回答 ID: {self.id} - アンケート: {self.survey.id}, 質問: {self.question.id}"