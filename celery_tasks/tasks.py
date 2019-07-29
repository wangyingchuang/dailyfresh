# 使用celery

import time
from dailyfresh import settings
from celery import  Celery

# 创建一个Celery类的实例对象
from django.core.mail import send_mail

# # 在任务一段加这几句代码
# import os
# import django
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dailyfresh.settings')
# django.setup()

app = Celery('celery_tasks.tasks', broker='redis://192.168.209.130:6379/8')

# 定义任务函数
@app.task
def send_register_active_email(to_email, username, token):
    """发送激活邮件"""
    # 发送邮件
    subject = '天天生鲜欢迎信息'
    message = ''
    sender = settings.EMAIL_FROM
    receiver = [to_email]
    html_message = '<h1>{0}, 欢迎您成为天天生鲜注册会员</h1>请点击下面链接激活您的账户<br/><a href="http://127.0.0.1:8000/user/active/{1}">http://127.0.0.1/user/active/{2}</a>'.format(
        username, token, token)
    send_mail(subject, message, sender, receiver, html_message=html_message)
    time.sleep(5)