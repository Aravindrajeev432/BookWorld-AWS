from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from carts.models import Cart
from accounts.models import Account, Address

from store.models import WishlistItem
from carts.models import CartItem
from orders.models import OrderProduct, banner
from store.models import Product, Product_Offer, Category_Offer
from category.models import Category
from django.views.decorators.cache import cache_control
from django.core.paginator import Paginator
from collections import Counter
from django.db.models import Count
from carts.views import _cart_id


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def index(request):
    try:
        uid = request.session['uid']
        is_user_blocked = Account.objects.get(id=uid)
        if is_user_blocked.is_blocked == True:
            return render(request, 'userblocked.html')
    except KeyError:
        uid = _cart_id(request)

        try:
            cart_id = Cart.objects.only('id').get(cart_id=uid)
            nonuser_cart = CartItem.objects.select_related(
                'product').filter(cart=cart_id.id).all()

            nonuser_cart_product_ids = []
            for uc in nonuser_cart:

                nonuser_cart_product_ids.append(uc.product.id)

            # print(nonuser_cart_product_ids)
        except BaseException:

            nonuser_cart_product_ids = []
    try:
        user_cart = CartItem.objects.filter(
            user=uid).select_related('product').all()

        user_cart_product_ids = []
        for uc in user_cart:

            user_cart_product_ids.append(uc.product.id)
            print("********")

        nonuser_cart_product_ids = []
    except BaseException:
        print("33")
        user_cart_product_ids = []
        try:

            if nonuser_cart_product_ids == []:

                nonuser_cart_product_ids = []
        except BaseException:

            nonuser_cart_product_ids = []
    # testannonimususer cart checking in landing

    ###
    cat = Category.objects.only('category_name').all()
    product_offer_details = {}
    category_offer_details = {}
    productoffers = Product_Offer.objects.select_related(
        'product').filter(active=True)

    for poffer in productoffers:

        product_offer_details.update({poffer.product.id: poffer.discount})
    categoryoffers = Category_Offer.objects.filter(active=True)
    for catoffers in categoryoffers:
        category_offer_details.update(
            {catoffers.category_id: catoffers.discount})
    try:
        wish = WishlistItem.objects.filter(user=uid).select_related('product')
    except BaseException:
        wish = []
    wishlist = []
    for w in wish:

        wishlist.append(w.product.id)
    pro = Product.objects.filter(
        is_active=True).defer(
        'description',
        'is_active').select_related("category").all().order_by('id')
    paginator = Paginator(pro, 6)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    # banner Section

    try:
        bannerimg = banner.objects.get(is_selected=True)
    except BaseException:
        bannerimg = ""
    context = {
        'category': cat,
        'pro': paged_products,
        'user_cart_product_ids': user_cart_product_ids,
        'nonuser_cart_product_ids': nonuser_cart_product_ids,
        'product_offer_details': product_offer_details,
        'category_offer_details': category_offer_details,
        'wishlist': wishlist,
        'bannerimg': bannerimg,

    }

    return render(request, 'landing.html', context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def home(request):
    pro = Product.objects.all()

    return render(request, 'landing.html', {'pro': pro})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def homepage(request):
    if 'email' in request.session:
        return render(request, 'home.html')
    else:
        return redirect('/')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def profile(request, id):

    try:
        uid = request.session['uid']
    except BaseException:
        return redirect('login')
    if uid != id:
        return redirect('profile', uid)
    user_details = Account.objects.get(id=id)

    try:
        user_address = Address.objects.get(user_id=id)

    except BaseException:
        user_address = " "

    f_cat = []
    fa_cat = user_details.ordered_product_user.all().select_related('product__category')

    for fav in fa_cat:
        print(fav)
        f_cat.append(fav.product.category_id)
    if len(fa_cat) == 0:
        
         fav_category_name = "Please Buy At Least One Book"

    else:

        c = Counter(f_cat)
        ca = c.most_common(1)

        fav_category_id = ca[0][0]
        fav_category = Category.objects.get(id=fav_category_id)

        fav_category_name = fav_category.category_name


   
    try:
        books_buyed = OrderProduct.objects.filter(
            user=id).values('user').annotate(
            count=Count('quantity'))
        books_buyed = list(books_buyed)
        books_buyed = books_buyed[0]
        books_buyed = books_buyed["count"]
    except BaseException:
        print("book_buyed exception")
        books_buyed = 0

    context = {
        'user': user_details,
        'fav_category': fav_category_name,
        'books_buyed': books_buyed,
        'user_address': user_address,
    }

    return render(request, 'user_profile.html', context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_address(request, id):
    uid = request.session['uid']

    if request.method == 'POST':
        address_line_1 = request.POST['address_line_1']
        address_line_2 = request.POST['address_line_2']
        country = request.POST['country']
        state = request.POST['state']
        city = request.POST['city']
        zipcode = request.POST['zipcode']
        print(address_line_1)
        print(address_line_2)
        print(country)
        print(state)
        print(city)
        print(zipcode)

        try:
            user_address = Address.objects.get(user_id=uid)
            user_address.address_line_1 = address_line_1
            user_address.address_line_2 = address_line_2
            user_address.country = country
            user_address.state = state
            user_address.city = city
            user_address.zipcode = zipcode
            user_address.save()
        except BaseException:
            user = Address(
                address_line_1=address_line_1,
                address_line_2=address_line_2,
                user_id=uid,
                country=country,
                state=state,
                city=city,
                zipcode=zipcode)
            user.save()

        return JsonResponse(
            {
                'success': True},

            safe=False

        )
    return JsonResponse(
        {
            'success': False},

        safe=False

    )


def editprofile(request, id):
    user_edit = Account.objects.get(id=id)

    if request.method == 'POST':
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        phone = request.POST['phone']

        user_edit.first_name = fname
        user_edit.last_name = lname
        user_edit.email = email
        user_edit.Phone_number = phone
        user_edit.save()

        return JsonResponse(
            {
                'success': True},

            safe=False

        )

    return JsonResponse(
        {
            'success': False},

        safe=False

    )


def wishlist(request):
    try:
        uid = request.session['uid']
        is_user_blocked = Account.objects.get(id=uid)
        if is_user_blocked.is_blocked == True:
            return render(request, 'userblocked.html')
    except KeyError:
        return redirect('login')
    try:
        user_cart = CartItem.objects.filter(user=uid).all()
        user_cart_product_ids = []
        for uc in user_cart:
          
            user_cart_product_ids.append(uc.product_id)
  
      
    except BaseException:
        user_cart_product_ids = []
    product_offer_details = {}
    category_offer_details = {}
    productoffers = Product_Offer.objects.filter(active=True)

    for poffer in productoffers:

        product_offer_details.update({poffer.product_id: poffer.discount})
    categoryoffers = Category_Offer.objects.filter(active=True)
    for catoffers in categoryoffers:
        category_offer_details.update(
            {catoffers.category_id: catoffers.discount})
    wish = WishlistItem.objects.filter(user=uid).select_related('product','product__category')
    wishlist = []
    for w in wish:
        wishlist.append(w.product_id)
    uid = request.session['uid']
    wish = WishlistItem.objects.filter(user_id=uid).select_related('product','product__category')

    category = Category.objects.all()
    context = {
        'wishlistitems': wish,
        'category': category,
        'user_cart_product_ids': user_cart_product_ids,
        'product_offer_details': product_offer_details,
        'category_offer_details': category_offer_details,
    }
    return render(request, 'wishlist.html', context)


def addwishlist(request, pid):
    print(pid)
    uid = request.session['uid']
    user = Account.objects.get(id=uid)
    product = Product.objects.get(id=pid)
    wish = WishlistItem(user=user, product=product)
    wish.save()

    return HttpResponse(pid)


def removewishlist(request, pid):
    print(pid)
    uid = request.session['uid']
    user = Account.objects.get(id=uid)
    product = Product.objects.get(id=pid)
    wish = WishlistItem.objects.get(user=user, product=product)
    wish.delete()
    return HttpResponse(pid)
