from django.db import models
from db.base_model import BaseModel

# Create your models here.


class OrderInfo(BaseModel):
    """订单信息模型类"""

    PAY_METHOD = {
        '1': '货到付款',
        '2': '微信支付',
        '3': '支付宝',
        '4': '银联支付',
    }

    PAY_METHOD_CHOICES = (
        (1, '货到付款'),
        (2, '微信支付'),
        (3, '支付宝'),
        (4, '银联支付'),
    )
    ORDER_STATUS = {
        '1': '待支付',
        '2': '待发货',
        '3': '待收货',
        '4': '待评价',
        '5': '已完成',
    }

    ORDER_STATUS_CHOICES = (
        (1, '待支付'),
        (2, '待发货'),
        (3, '待收货'),
        (4, '待评价'),
        (5, '已完成'),
    )

    order_id = models.CharField(max_length=20, primary_key=True, verbose_name='订单编号')
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, verbose_name='用户')
    address = models.ForeignKey('user.Address', on_delete=models.CASCADE, verbose_name='地址')
    pay_method = models.SmallIntegerField(default=3, choices=PAY_METHOD_CHOICES, verbose_name='支付方式')
    total_count = models.IntegerField(default=1, verbose_name='商品数量')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品总价')
    transit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='运费')
    order_status = models.SmallIntegerField(default=1, choices=ORDER_STATUS_CHOICES, verbose_name='订单状态')
    trade_no = models.CharField(max_length=20, default='', verbose_name='支付编号')

    class Meta:
        db_table = 'df_order_info'
        verbose_name = '订单信息'
        verbose_name_plural = verbose_name

class OrderGoods(BaseModel):
    """订单商品模型类"""
    order = models.ForeignKey('OrderInfo', on_delete=models.CASCADE, verbose_name='订单')
    sku = models.ForeignKey('goods.GoodsSKU', on_delete=models.CASCADE, verbose_name='商品SKU')
    count = models.IntegerField(default=1, verbose_name='商品数目')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品价格')
    comment = models.CharField(max_length=256, default='', verbose_name='评论')

    class Meta:
        db_table = 'df_order_goods'
        verbose_name = '订单商品'
        verbose_name_plural = verbose_name