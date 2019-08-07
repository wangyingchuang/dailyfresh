import os
import traceback
import requests
from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.domain.AlipayTradePagePayModel import AlipayTradePagePayModel
from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest
from alipay.aop.api.request.AlipayTradeQueryRequest import AlipayTradeQueryRequest
from alipay.aop.api.response.AlipayTradePagePayResponse import AlipayTradePagePayResponse
from alipay.aop.api.response.AlipayTradePayResponse import AlipayTradePayResponse
from django.conf import settings
from django.test import TestCase
import django, json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dailyfresh.settings')
# django.setup()
# Create your tests here.

transit_price = 10
order_id = '201911'
total_price = 20

"""
设置配置，包括支付宝网关地址、app_id、应用私钥、支付宝公钥等，其他配置值可以查看AlipayClientConfig的定义。
"""
alipay_client_config = AlipayClientConfig()
alipay_client_config.server_url = 'https://openapi.alipaydev.com/gateway.do'
alipay_client_config.app_id = '2016100100641374'
app_private_key = ''
with open(os.path.join(settings.BASE_DIR, 'apps/order/app_private_key.pem'), 'r') as f:
    for line in f:
        app_private_key += line
alipay_client_config.app_private_key = app_private_key
alipay_public_key = ''
with open(os.path.join(settings.BASE_DIR, 'apps/order/alipay_public_key.pem'), 'r') as f:
    for line in f:
        alipay_public_key += line
alipay_client_config.alipay_public_key = alipay_public_key
"""
得到客户端对象。
注意，一个alipay_client_config对象对应一个DefaultAlipayClient，定义DefaultAlipayClient对象后，alipay_client_config不得修改，如果想使用不同的配置，请定义不同的DefaultAlipayClient。
logger参数用于打印日志，不传则不打印，建议传递。
"""
client = DefaultAlipayClient(alipay_client_config=alipay_client_config)

total_pay = transit_price + total_price
model = AlipayTradePagePayModel()
model.out_trade_no = order_id
model.total_amount = 0.01
model.subject = "天天生鲜{0}".format(order_id)
model.product_code = "FAST_INSTANT_TRADE_PAY"
request = AlipayTradePagePayRequest(biz_model=model)

response = client.page_execute(request, http_method="GET")
print(response)


# request = AlipayTradeQueryRequest(biz_model=model)
# response = client.page_execute(request, http_method="GET")
# data = requests.get(response)
# print(json.loads(data.text))
# data = json.loads(data.text)
# print(data.get('alipay_trade_query_response').get('code'))
