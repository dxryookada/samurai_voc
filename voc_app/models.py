from django.db import models

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

# --- アンケートテーブル --- #
class Survey(models.Model):
    gender = models.ForeignKey(Gender, verbose_name="性別", on_delete=models.CASCADE)
    age_group = models.ForeignKey(AgeGroup, verbose_name="年代", on_delete=models.CASCADE)
    question1 = models.IntegerField(verbose_name="質問1", null=False)
    question2 = models.IntegerField(verbose_name="質問2", null=False)
    question3 = models.IntegerField(verbose_name="質問3", null=False)
    question4 = models.IntegerField(verbose_name="質問4", null=False)
    question5 = models.IntegerField(verbose_name="質問5", null=False)
    free_text = models.TextField(verbose_name="自由記入欄", blank=True, null=True)
    free_text_ai_rating = models.IntegerField(verbose_name="自由記入欄AI評価", blank=True, null=True)
    submitted_at = models.DateField(verbose_name="投稿日", auto_now_add=True)

    class Meta:
        verbose_name = 'アンケート内容'
        verbose_name_plural = 'アンケート一覧'

    def __str__(self):
        return f"アンケート ID: {self.id}"

# --- 工事テーブル --- #
class Work(models.Model):
    survey = models.ForeignKey(Survey, verbose_name="アンケート", on_delete=models.SET_NULL, null=True, blank=True)
    receipt_number = models.IntegerField(verbose_name="受付番号", unique=True)
    receipt_date = models.DateTimeField(verbose_name="受付日", null=False)
    work_start_date = models.DateField(verbose_name="作業開始日", null=False)
    url_token = models.CharField(verbose_name="URLトークン", max_length=255, unique=True)
    url_token_expiry = models.DateField(verbose_name="URLトークン期限", null=False)

    class Meta:
        verbose_name = '工事情報'
        verbose_name_plural = '工事一覧'

    def __str__(self):
        formatted_number = f"{self.receipt_number:06}"
        return f"工事 ID: {self.id} (受付番号: {formatted_number})"
