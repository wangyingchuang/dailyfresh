from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic.base import View
from django_redis import get_redis_connection

from apps.goods.models import GoodsSKU
from utils.mixin import LoginRequiredMixin




# Create your views here.

# 请求方式：ajax post
# 传递参数：商品id sku_id ,商品数量 count
# 返回： JsonResponse({'res':5, 'message': '添加成功', 'total_count': total_count})
# /cart/add


class CartAddView(View):
    """购物车记录添加"""
    def post(self, request):
        """购物车记录添加"""
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res':0, 'errmsg': '请先登录'})

        # 接收数据
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')

        # 数据校验
        if not all([sku_id, count]):
            return JsonResponse({'res':1, 'errmsg': '数据不完整'})

        # 校验添加商品的数量
        try :
            count = int(count)
        except Exception as e:
            return JsonResponse({'res':2, 'errmsg': '商品数量出错'})

        # 校验商品是否存在
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'res':3, 'errmsg': '商品不存在'})

        # 业务处理：添加购物车记录
        conn = get_redis_connection('default')
        cart_key = 'cart_{0}'.format(user.id)
        cart_count = conn.hget(cart_key, sku_id)
        if cart_count:
            count += int(cart_count)

        # 校验商品的库存
        if count > sku.stock:
            return JsonResponse({'res':4, 'errmsg': '商品库存不足'})
        conn.hset(cart_key, sku_id, count)
        # 获取商品条目数
        total_count = conn.hlen(cart_key)

        # 返回应答
        return JsonResponse({'res':5, 'message': '添加成功', 'total_count': total_count})


# /cart
class CartInfoView(LoginRequiredMixin, View):
    """显示购物车页面"""
    def get(self, request):
        """显示"""
        # 获取登录的用户
        user = request.user

        # 获取用户购物车中的商品信息
        conn = get_redis_connection('default')
        cart_key = 'cart_{0}'.format(user.id)
        cart_dict = conn.hgetall(cart_key)

        skus = list()
        total_count = 0
        total_price = 0
        # 遍历获取的商品的信息
        for sku_id, count in cart_dict.items():
            sku = GoodsSKU.objects.get(id=sku_id)
            # 计算商品小计
            count = count.decode()
            amount = sku.price * int(count)
            # 动态给sku对象添加一个amount属性和count属性
            sku.amount = amount
            sku.count = count
            skus.append(sku)

            # 计算商品的总数量和总价格
            total_count += int(count)
            total_price += amount

        # 组织上下文
        context = {
            'total_count': total_count,
            'total_price': total_price,
            'skus': skus,
        }

        # 使用模板，返回页面
        return render(request, 'cart.html', context)


# 请求方式：ajax post
# 传递参数：商品id sku_id ,商品数量 count
# 返回： JsonResponse({'res':5, 'message': '更新成功', 'total_count': total_count})
# /cart/update
class CartUpdateView(View):
    """购物车记录更新"""
    def post(self, request):
        """购物车记录更新"""
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '请先登录'})

        # 接收数据
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')

        # 数据校验
        if not all([sku_id, count]):
            return JsonResponse({'res': 1, 'errmsg': '数据不完整'})

        # 校验添加商品的数量
        try:
            count = int(count)
        except Exception as e:
            return JsonResponse({'res': 2, 'errmsg': '商品数量出错'})

        # 校验商品是否存在
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'res': 3, 'errmsg': '商品不存在'})

        # 业务处理：更新购物车记录
        conn = get_redis_connection('default')
        cart_key = 'cart_{0}'.format(user.id)

        # 校验商品的库存
        if count > sku.stock:
            return JsonResponse({'res': 4, 'errmsg': '商品库存不足'})

        conn.hset(cart_key, sku_id, count)

        # 计算商品的总件数
        total_count = 0
        vals = conn.hvals(cart_key)
        for val in vals:
            total_count += int(val)
        # 返回应答
        return JsonResponse({'res': 5, 'message': '更新成功', 'total_count': total_count})


# 请求方式：ajax post
# 传递参数：商品id sku_id
# 返回： JsonResponse({'res':5, 'message': '删除成功'} )
# /cart/delete
class CartDeleteView(View):
    """购物车记录删除"""
    def post(self, request):
        """购物车记录删除"""
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '请先登录'})

        # 接收数据
        sku_id = request.POST.get('sku_id')


        # 数据校验
        if not sku_id:
            return JsonResponse({'res': 1, 'errmsg': '数据不完整'})

        # 校验商品是否存在
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'res': 2, 'errmsg': '商品不存在'})

        # 业务处理：删除购物车记录
        conn = get_redis_connection('default')
        cart_key = 'cart_{0}'.format(user.id)

        conn.hdel(cart_key, sku_id)

        # 计算商品的总件数
        total_count = 0
        vals = conn.hvals(cart_key)
        for count in vals:
            total_count += int(count)

        # 返回应答
        return JsonResponse({'res': 5, 'message': '删除成功', 'total_count': total_count})