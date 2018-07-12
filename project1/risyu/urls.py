from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    url('^login', views.login, name='login'),
    url('', views.index, name='index'),
    # # パラメータあり
    # path('<param>/', views.index_param, name='index_param'),
    # # パラメータなし
    # path('', views.index_template, name='index_template'),
]
