from datetime import date

from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.cache import cache_control
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Sum
from django.http import HttpResponse
from django.db.models import Q


from accounts.models import Address, Account
from orders.models import Order
from . models import Cart, CartItem
from store.models import Product_Offer, Category_Offer, Product, Coupon



def cart(request, total=0, quantity=0, cart_items=None):

    if 'first_name' in request.session:

        # product_offer_details=Product_Offer.objects.all()
        p_o_d = {}
        c_o_d = {}
        # product offer details
        try:
            uid = request.session['uid']

            user = request.user
            # cart_items=CartItem.objects.filter(user=user,is_active=True)
            cart_items = CartItem.objects.filter(Q(user_id=uid) & Q(is_active=True)).order_by(
                'id').select_related('product', 'product__category')
            
            for cart_item in cart_items:
                total += (cart_item.total_after_discount)
                quantity += cart_item.quantity

                try:
                    prod_discount = Product_Offer.objects.get(product_id=cart_item.product_id)

                    p_o_d.update({prod_discount.product_id: prod_discount.discount})
                except BaseException:
                    pass
                try:

                    cat_discount = Category_Offer.objects.get(category_id=cart_item.product.category_id)
                    c_o_d.update(
                        {cat_discount.category_id: cat_discount.discount})
                except BaseException:
                    pass
        except ObjectDoesNotExist:

            pass
        context = {
            'total': total,
            'quantity': quantity,
            'cart_items': cart_items,
            'p_o_d': p_o_d,
            'c_o_d': c_o_d,
            'cart_id': uid,
        }
        return render(request, 'store/cart.html', context)

    else:
        try:

            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_id = cart.id
            cart_items = CartItem.objects.filter(
                cart=cart, is_active=True).select_related('product').select_related('product', 'product__category')

            for cart_item in cart_items:
                total += (cart_item.product.price * cart_item.quantity)
                quantity += cart_item.quantity
        except ObjectDoesNotExist:

            pass
            cart_id = ""
        context = {
            'total': total,
            'quantity': quantity,
            'cart_items': cart_items,
            'cart_id': cart_id,
        }
        return render(request, 'store/cart.html', context)


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    request.session['coupon_code'] = ""
    request.session['coupon_id'] = ""
    request.session['coupon_discount'] = 0
    product = Product.objects.get(id=product_id)
    cat_id = product.category.id
    try:
        pro_discount_rate = Product_Offer.objects.get(product_id=product_id)
    except BaseException:
        pass
    try:

        cat_discount_rate = Category_Offer.objects.get(category_id=cat_id)
    except BaseException:
        pass

    try:
        if pro_discount_rate.discount < cat_discount_rate.discount:
            discount_rate = cat_discount_rate.discount
            discount_type = "cat"
            total_after_discount = product.price - \
                ((discount_rate / 100) * product.price)
        else:
            discount_rate = pro_discount_rate.discount
            discount_type = "pro"
            total_after_discount = product.price - \
                ((discount_rate / 100) * product.price)
    except BaseException:

        try:
            if cat_discount_rate:
                try:
                    if not pro_discount_rate:
                        pass
                except BaseException:
                    discount_rate = cat_discount_rate.discount
                    discount_type = "cat"
                    total_after_discount = product.price - \
                        ((discount_rate / 100) * product.price)

        except BaseException:
            try:
                if pro_discount_rate:
                    try:
                        if not cat_discount_rate:
                            pass
                    except BaseException:
                        discount_rate = pro_discount_rate.discount
                        discount_type = "pro"
                        total_after_discount = product.price - \
                            ((discount_rate / 100) * product.price)
            except BaseException:

                discount_rate = 0
                discount_type = "none"
                total_after_discount = product.price

    try:
        if 'uid' in request.session:
            pass
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        if 'uid' in request.session:
            pass
        else:
            cart = Cart.objects.create(
                cart_id=_cart_id(request)
            )
            cart.save()
    try:
        if 'uid' in request.session:
            uid = request.session['uid']
            cart_item = CartItem.objects.get(product=product, user_id=uid)
        else:

            cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.quantity += 1
        cart_item.total_after_discount = product.price
        cart_item.save()

    except CartItem.DoesNotExist:
        if 'uid' in request.session:
            uid = request.session['uid']
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                user_id=uid,
                discount=discount_rate,
                discounttype=discount_type,
                total_after_discount=total_after_discount
            )
        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart,
                total_after_discount=product.price
            )
            cart_item.save()
    return redirect('cart')


def add_cart_from_cart(request, product_id):

    product = Product.objects.get(id=product_id)

    try:
        if 'uid' in request.session:
            pass
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        if 'uid' in request.session:
            pass
        else:
            cart = Cart.objects.create(
                cart_id=_cart_id(request)
            )
            cart.save()
    try:
        if 'uid' in request.session:
            uid = request.session['uid']
            cart_item = CartItem.objects.get(product=product, user_id=uid)
        else:

            cart_item = CartItem.objects.get(product=product, cart=cart)

        cart_item.quantity += 1
        qty = cart_item.quantity
        cart_item.total_after_discount = (
            qty * product.price) - ((cart_item.discount / 100) * (qty * product.price))
        cart_item.save()

    except CartItem.DoesNotExist:
        if 'uid' in request.session:
            uid = request.session['uid']
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                user_id=uid
            )
        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart,
            )
            qty = 1
            cart_item.save()

    return HttpResponse(qty)


def cart_total_finder(request, id):
    if 'uid' in request.session:
        uid = request.session['uid']

        total = CartItem.objects.filter(
            user_id=uid).aggregate(
            Sum('total_after_discount'))

        return HttpResponse(total['total_after_discount__sum'])
    else:

        total = CartItem.objects.filter(
            cart_id=id).aggregate(
            Sum('total_after_discount'))

        return HttpResponse(total['total_after_discount__sum'])


def remove_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if 'uid' in request.session:
        uid = request.session['uid']
        cart_item = CartItem.objects.get(product=product, user_id=uid)
    else:

        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        qty = cart_item.quantity
        cart_item.total_after_discount = (
            qty * product.price) - ((cart_item.discount / 100) * (qty * product.price))
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')


def remove_cart_from_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if 'uid' in request.session:
        uid = request.session['uid']
        cart_item = CartItem.objects.get(product=product, user_id=uid)
    else:

        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        qty = cart_item.quantity
        cart_item.total_after_discount = (
            qty * product.price) - ((cart_item.discount / 100) * (qty * product.price))
        cart_item.save()
    else:
        cart_item.delete()
    return HttpResponse(qty)


def delete_cart(request, product_id):
    if 'uid' in request.session:
        uid = request.session['uid']
        product = get_object_or_404(Product, id=product_id)
        cart_item = CartItem.objects.get(product=product, user_id=uid)
    else:

        cart = Cart.objects.get(cart_id=_cart_id(request))
        product = get_object_or_404(Product, id=product_id)
        cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart')

    # chekout


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def checkout(request, total=0, quantity=0, cart_items=None):

    try:
        if 'uid' in request.session:
            uid = request.session['uid']

            ca_count = CartItem.objects.filter(
                user_id=uid, is_active=True).count()
            cart_items = CartItem.objects.filter(user_id=uid, is_active=True)

            # checking for empty queryset

            if ca_count == 0:
                return redirect('home')
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.total_after_discount)
            quantity += cart_item.quantity

        if total == 0:
            return redirect('index')
        try:
            coupon_discount = request.session['coupon_discount']

            if coupon_discount == 0:
                discount = 0
                total_after_coupon = total
            else:
                discount = request.session['coupon_discount']
                total_after_coupon = total - discount

        except BaseException:
            discount = 0
            total_after_coupon = total
    except ObjectDoesNotExist:

        return redirect('home')

    try:
        user_details = Account.objects.get(id=uid)

    except BaseException:

        user_details = " "
    try:
        user_address = Address.objects.get(user_id=uid)

        user_address_status = True

    except BaseException:
        user_address = ""

        user_address_status = False

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'user_address': user_address,
        'user_details': user_details,
        'user_address_status': user_address_status,
        'coupon_discount': discount,
        'total_after_coupon': total_after_coupon
    }
    return render(request, 'store/checkout.html', context)


def couponCheck(request, coupon):

    try:
        coupon_details = Coupon.objects.get(coupon_code=coupon)

        discount = coupon_details.discount
        request.session['coupon_discount'] = discount
        request.session['coupon_code'] = coupon
        request.session['coupon_id'] = coupon_details.id

    except BaseException:

        discount = 0
        request.session['coupon_discount'] = 0
        request.session['coupon_code'] = ""
        request.session['coupon_id'] = ""

    coupon_count = Coupon.objects.filter(coupon_code__exact=coupon).count()

    if coupon_count == 1:
        coupon_details = Coupon.objects.get(coupon_code=coupon)

        current_date = date.today()

        if current_date <= coupon_details.valid_to.date(
        ) and current_date >= coupon_details.valid_from.date():

            uid = request.session['uid']
            if Order.objects.filter(Q(user_id=uid) & Q(
                    coupon_id=coupon_details.id) & Q(is_ordered=True)).exists():
                discount = 0

                return HttpResponse(discount)
            else:

                return HttpResponse(discount)
        else:

            discount = 0
            return HttpResponse(discount)
    else:

        discount = 0
        return HttpResponse(discount)
