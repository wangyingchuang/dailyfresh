from django.core.paginator import Paginator
from django.shortcuts import render, redirect, reverse
from django.views.generic.base import View
from django_redis import get_redis_connection
from django.core.cache import cache
from apps.goods.models import GoodsType, IndexGoodsBanner, IndexTypeGoodsBanner, IndexPromotionBanner, GoodsSKU
from apps.order.models import OrderGoods

# Create your views here.


# goods/index
class IndexView(View):
    """首页"""

    def get(self, request):
        """首页"""
        # 获取用户信息
        user = request.user

        # 判断缓存
        try:
            context = cache.get('index_page_data')
        except Exception as e:
            context = None

        if context is None:
            # 没有缓存数据
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
                'promotion_banners': promotion_banners,
            }
            # 设置缓存
            cache.set('index_page_data', context, 3600)

        # 获取购物车中商品数量
        cart_count = 0
        if user.is_authenticated:
            # 用户已登录
            conn = get_redis_connection('default')
            cart_key = 'cart_{0}'.format(user.id)
            cart_count = conn.hlen(cart_key)

        context.update(user=user, cart_count=cart_count)

        return render(request, 'index.html', context)


# goods/detail/sku_id
class DetailView(View):
    """详情页面"""
    def get(self, request, goods_id):
        """显示详情页面"""
        # 获取商品SKU信息
        try :
            sku = GoodsSKU.objects.get(id=goods_id)
        except GoodsSKU.DoesNotExist:
            return redirect(reverse('goods:detail'))

        # 获取商品的分类信息
        types = GoodsType.objects.all()

        # 获取商品的评论信息
        sku_orders = OrderGoods.objects.filter(sku=sku)

        # 获取新商信息
        new_skus = GoodsSKU.objects.filter(type=sku.type).order_by('-create_time')[:2]

        # 获取同一个SPU的商品
        same_spu_skus = GoodsSKU.objects.filter(goods_spu=sku.goods_spu).exclude(id=goods_id)

        # 获取用户购物车中的商品数目
        user = request.user
        cart_count = 0
        if user.is_authenticated:
            # 用户已登录
            conn = get_redis_connection('default')
            cart_key = 'cart_{}'.format(user.id)
            cart_count = conn.hlen(cart_key)

            # 添加用户的历史浏览记录
            conn = get_redis_connection('default')
            history_key = 'history_{}'.format(user.id)
            conn.lrem(history_key, 0, goods_id)
            conn.lpush(history_key, goods_id)
            # 只保存用户的最新浏览的5条信息
            conn.ltrim(history_key, 0, 4)

        # 组织上下文
        context = {
            'sku':sku,
            'types': types,
            'sku_orders': sku_orders,
            'new_skus': new_skus,
            'same_spu_skus': same_spu_skus,
            'cart_count': cart_count,
        }

        # 使用模板
        return render(request, 'detail.html', context)


# goods/list/type_id/页码?sort=排序方式
class ListView(View):
    """列表页"""
    def get(self, request, type_id, page):
        """显示列表页"""
        # 获取种类信息
        try:
            type = GoodsType.objects.get(id=type_id)
        except GoodsType.DoesNotExist :
            return redirect(reverse('goods:index'))
        # 获取排序方式
        # sort=default 按照默认id排序
        # sort=price 按照商品价格排序
        # sort=hot 按照商品销量排序
        sort = request.GET.get('sort')
        if sort == 'price':
            skus = GoodsSKU.objects.filter(type=type).order_by('price')
        elif sort == 'hot':
            skus = GoodsSKU.objects.filter(type=type).order_by('-sales')
        else:
            sort = 'default'
            skus = GoodsSKU.objects.filter(type=type).order_by('-id')

        # 对商品进行分页s
        paginator = Paginator(skus, 1)

        # 获取第page页的内容
        try:
            page = int(page)
        except Exception as e:
            page = 1
        if page > paginator.num_pages:
            page = 1

        # 获取第page页的paginator.page实例对象
        skus_page = paginator.page(page)

        # todo: 进行页码控制， 页面上最多显示5个页面
        num_pages = paginator.num_pages
        if num_pages < 5:
            pages = range(1, num_pages + 1)
        elif page <= 3:
            pages = range(1, 6)
        elif num_pages - page <= 2:
            pages = range(num_pages - 4, num_pages + 1)
        else:
            pages = range(page - 2, page + 3)

        # 获取商品的分类信息
        types = GoodsType.objects.all()

        # 获取新商信息
        new_skus = GoodsSKU.objects.filter(type=type).order_by('-create_time')[:2]

        # 获取用户购物车中的商品数目
        user = request.user
        cart_count = 0
        if user.is_authenticated:
            # 用户已登录
            conn = get_redis_connection('default')
            cart_key = 'cart_{}'.format(user.id)
            cart_count = conn.hlen(cart_key)

        # 组织上下文
        context = {
            'type': type,
            'skus_page': skus_page,
            'types': types,
            'new_skus': new_skus,
            'cart_count': cart_count,
            'sort': sort,
            'pages': pages,
        }


        return render(request, 'list.html', context)