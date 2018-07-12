from django.db import models
from django import forms


# Create your models here.
# ログインフォーム
class LoginForm(forms.Form):
    id_field = forms.CharField(label='ID',
            error_messages={'required': ""},
            widget=forms.TextInput(
                attrs={'placeholder':'kからはじまるIDを入力', 'class':'form-control'})
    )
    passwd_field = forms.CharField(label='PassWord',
            error_messages={'required': ""},
            widget=forms.PasswordInput(
                attrs={'placeholder':'パスワードを入力', 'class':'form-control'})
    )