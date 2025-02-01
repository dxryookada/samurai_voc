from django import forms

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(label="CSVファイルを選択")

class PasswordResetForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'メールアドレスを入力してください',
        }),
        label="メールアドレス"
    )