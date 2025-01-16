from django import forms
from .models import Survey, Question, Choice

class SurveyForm(forms.ModelForm):
    question_fields = []

    class Meta:
        model = Survey
        fields = ['gender', 'age_group', 'free_text']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 質問フィールドが既に追加されているか確認
        if not hasattr(self, '_questions_initialized'):

            # 質問内容を動的に追加
            for question in Question.objects.all():
                field_name = f'question{question.order}'
                self.fields[f'question{question.order}'] = forms.ModelChoiceField(
                    queryset=Choice.objects.filter(question=question),
                    widget=forms.RadioSelect,
                    empty_label=None,
                    label=question.content,
                )
                self.question_fields.append(self[field_name])

            # 初期化済みフラグを設定
            self._questions_initialized = True