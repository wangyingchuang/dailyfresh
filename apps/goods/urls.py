from django.urls import path

from apps.goods import views

app_name = 'goods'
urlpatterns = [
    path('', views.index, name='index'),
]
