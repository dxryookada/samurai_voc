import csv
from django.db import transaction
from django.core.management.base import BaseCommand
from your_app.models import Work, CustomUser, ConstructionWorker

class Command(BaseCommand):
    help = "工事情報CSVを読み込み、データベースに登録または更新します。"

    def handle(self, *args, **kwargs):
        csv_path = "/path/to/work_csv.csv"  # CSVファイルのパス
        try:
            with open(csv_path, encoding='utf-8') as csv_file:
                reader = csv.DictReader(csv_file, delimiter=',')

                # データ整合性を保つためにトランザクションを使用
                with transaction.atomic():
                    for row in reader:
                        # 工事テーブルから受付番号を元に取得
                        work = Work.objects.filter(
                            receipt_number=row['受付番号'],
                            receipt_date=row['受付日時']
                        ).first()

                        # 工事情報が見つからない場合はスキップまたはエラー処理
                        if not work:
                            self.stderr.write(f"受付番号 {row['受付番号']} の工事情報が見つかりません")
                            continue

                        # 要員１の従業員情報を取得
                        employee_1 = CustomUser.objects.filter(employee_id=row['要員ＩＤ１']).first()
                        if employee_1:
                            ConstructionWorker.objects.update_or_create(
                                construction=work,
                                employee=employee_1,
                            )
                        else:
                            self.stderr.write(f"要員ＩＤ１ {row['要員ＩＤ１']} に該当する従業員が見つかりません")

                        # 要員２の従業員情報を取得
                        employee_2 = CustomUser.objects.filter(employee_id=row['要員ＩＤ２']).first()
                        if employee_2:
                            ConstructionWorker.objects.update_or_create(
                                construction=work,
                                employee=employee_2,
                            )
                        else:
                            self.stderr.write(f"要員ＩＤ２ {row['要員ＩＤ２']} に該当する従業員が見つかりません")

            self.stdout.write(self.style.SUCCESS("工事情報CSVの処理が完了しました"))
        except Exception as e:
            self.stderr.write(f"エラーが発生しました: {e}")
