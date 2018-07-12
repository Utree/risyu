from django.shortcuts import render
from django.http.response import HttpResponse, HttpResponseRedirect
# ログインページのモデル
from .models import LoginForm
# ログインモジュール
from .login import auth
from .choice_test import main

# sqlite3 setup
import sqlite3

# dir
import os

# databaseのパス
dbpath = os.path.dirname(os.path.abspath(__file__)) + '/syllabus.sqlite'

# Create your views here.
# ログインページ
def login(request):
    # loginしているかどうかを確認
    try:
        request.session['id']
        return HttpResponseRedirect('/')
    # sessionに記録がなければアクセスさせない
    except KeyError:
        pass
    # レスポンス用の変数はココで定義
    loggedIn = False
    message = ' '
    l = LoginForm(data=request.POST)

    # ログイン処理
    if request.method == 'POST':
        if l.is_valid() == True:
            # idとpasswdをlogin.pyに投げる
            result = auth(request.POST['id_field'], request.POST['passwd_field'])

            # 結果を変数に入れる
            # 成功時：loggedIn=True,失敗時：loggedIn=False
            loggedIn = result[0]
            # 成功時：message=ユーザー名,ログイン失敗時：message=Login Failed,生徒以外のログイン時：message=You can not access
            message = result[1]

            # ログイン成功時
            if result[0]:
                request.session['id'] = request.POST['id_field']
                request.session['pass'] = message
                return HttpResponseRedirect('/')
            # ログイン失敗時
            else:
                pass

    # ログアウト処理
    if 'logout' in request.POST:
        request.session.clear()

    return render(request, 'risyu/login.html', {
        'message': message,
        'login_form': l,
    })

def index(request):
    # loginしているかどうかを確認
    try:
        request.session['id']
    # sessionに記録がなければアクセスさせない
    except KeyError:
        return HttpResponseRedirect('/login/')
    # 検索結果を持たせるリスト
    response_list = []
    response_jikanwari = []
    preset, search_ans = main(request.session['pass'])

    search_ans = preset + search_ans


    for i in range(len(search_ans)):
        response_list.append([str(search_ans[i][16]), str(search_ans[i][9]), str(search_ans[i][1] + ' ' + search_ans[i][4] + ' ' + search_ans[i][16])])

    youbi = ['月', '火', '水', '木', '金']
    for i in range(7):
        for j in range(len(youbi)):
            response_jikanwari.append(youbi[j] + str(i+1))

    return render(request, 'risyu/index.html', {
        "jikanwari": response_jikanwari,
        "class_list": response_list,
    },)


# # Create your views here.
# def index_param(request, param):
#     # html_fileへの値の渡し方
#     response = {
#         'param1': param
#     }
#
#     return render(request, 'param.html', response)
#
# def index_template(request):
#     return render(request, 'index.html')
