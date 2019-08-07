# 使用celery

# # 在任务一段加这几句代码
# import os
# import django
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dailyfresh.settings')
# django.setup()
import os
import time

from django.template import loader

from dailyfresh import settings
from celery import  Celery
from django_redis import get_redis_connection

from apps.goods.models import GoodsType, IndexGoodsBanner, IndexTypeGoodsBanner, IndexPromotionBanner
# 创建一个Celery类的实例对象
from django.core.mail import send_mail
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


@app.task
def generate_static_index_html():
    """产生首页静态页面"""

    # 获取商品种类信息
    types = GoodsType.objects.all()

    # 获取首页轮播商品信息
    goods_banners = IndexGoodsBanner.objects.all().order_by('index')

    # 获取首页促销商品信息
    promotion_banners = IndexPromotionBanner.objects.all().order_by('index')

    # 获取分类商品展示信息
    for type in types:
        image_goods_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1)
        font_goods_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0)
        type.image_goods_banners = image_goods_banners
        type.font_goods_banners = font_goods_banners

    # 组织上下文
    context = {
        'types': types,
        'goods_banners': goods_banners,
        'promotion_goods': promotion_banners,
    }

    # s使用模板
    # 1. 加载模板文件，返回模板对象
    temp = loader.get_template('static_index.html')
    # 2. 渲染模板
    static_index_html = temp.render(context)

    # 生成对应静态文件
    save_path = os.path.join(settings.BASE_DIR, 'static/index.html')
    with open(save_path, 'w') as f:
        f.write(static_index_html)