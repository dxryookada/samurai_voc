from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class CustomUserManager(BaseUserManager):
    def create_user(self, employee_id, name, email, password=None, **extra_fields):
        if not email:
            raise ValueError('メールアドレス情報が必要です')
        email = self.normalize_email(email)
        user = self.model(employee_id=employee_id, name=name, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, employee_id, name, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('スーパーユーザーはis_staff=Trueでなければなりません。')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('スーパーユーザーはis_superuser=Trueでなければなりません。')
        return self.create_user(employee_id, name, email, password, **extra_fields)

# --- 従業員テーブル --- #
class CustomUser(AbstractBaseUser, PermissionsMixin):
    employee_id = models.CharField(verbose_name='従業員ID',max_length=50, unique=True)
    work_area = models.ForeignKey('WorkArea', verbose_name='作業エリア', on_delete=models.CASCADE, default=1)
    name = models.CharField(verbose_name='お名前', max_length=100)
    email = models.EmailField(verbose_name='メールアドレス',unique=True)
    is_staff = models.BooleanField(verbose_name='管理者権限', default=False)  # 管理者権限
    is_active = models.BooleanField(verbose_name='実行権限', default=True)
    advice = models.TextField(verbose_name='AIアドバイス', blank=True, null=True)  # AIアドバイス
    login_remember_until = models.DateTimeField(verbose_name='ログイン記憶', blank=True, null=True)  # ログイン記憶
    login_lock_until = models.DateTimeField(verbose_name='ログインロック', blank=True, null=True)  # ログインロック

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['employee_id', 'name']

    class Meta:
        verbose_name = '従業員情報'
        verbose_name_plural = '従業員一覧'

    def __str__(self):
        return self.email
    
# --- 作業エリアテーブル --- #
class WorkArea(models.Model):
    name = models.CharField(verbose_name='作業エリア', max_length=100, unique=True)  # 作業エリアの名前

    class Meta:
        verbose_name = '作業エリア'
        verbose_name_plural = '作業エリア一覧'

    def __str__(self):
        return self.name

# --- 表彰テーブル --- #
class AwardType(models.Model):
    name = models.CharField(verbose_name='表彰種類', max_length=50, unique=True)  # 金・銀・銅など

    class Meta:
        verbose_name = '表彰内容'
        verbose_name_plural = '表彰一覧'

    def __str__(self):
        return self.name

# --- 表彰回数テーブル --- #
class AwardCount(models.Model):
    employee = models.ForeignKey(CustomUser, verbose_name='従業員', on_delete=models.CASCADE)  # 従業員への外部キー
    award_type = models.ForeignKey(AwardType, verbose_name='表彰種類', on_delete=models.CASCADE)  # 表彰種類への外部キー

    class Meta:
        verbose_name = '表彰回数情報'
        verbose_name_plural = '表彰回数一覧'
    
    def __str__(self):
        return f"{self.employee.name} - {self.award_type.name}"

# --- 工事作業員テーブル --- #
class ConstructionWorker(models.Model):
    employee = models.ForeignKey(CustomUser, verbose_name='従業員', on_delete=models.CASCADE)  # 従業員への外部キー
    construction = models.ForeignKey('voc_app.Work', verbose_name='工事', on_delete=models.CASCADE)  # 工事テーブルへの外部キー

    class Meta:
        verbose_name = '工事作業員情報'
        verbose_name_plural = '工事作業員一覧'

    def __str__(self):
        return f"{self.employee.name} - {self.construction.id}"