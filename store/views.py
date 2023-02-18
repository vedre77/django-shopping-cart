from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from .models import Product
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id

# Create your views here.
def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug != None:
        # list category products
        categories = get_object_or_404(Category, slug=category_slug) 
        products = Product.objects.filter(category=categories, is_available=True).order_by('id')
        paginator = Paginator(products, 1)
        page = request.GET.get('page')
        # we store the single product per page:
        paged_products = paginator.get_page(page)
        product_count = products.count()
    else:
        # list all products
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(products, 3)
        page = request.GET.get('page')
        # we store the 6 products per page:
        paged_products = paginator.get_page(page)
        product_count = products.count()

    context = {
        'products': paged_products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)

def product_detail(request, category_slug, product_slug):
    try:
    # We use a double underscore to refer to the property of some related object in a django query:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
    # we need to check if the viewed product is in cart, so we check if the product is connected
    # to the cart via the CartItem model:
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e

    context = {
        'single_product': single_product,
        'in_cart': in_cart,
    }
    return render(request, 'store/product_detail.html', context)

def search(request):
    # get keyword from the GET request
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        # check for blank
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()
    context = {
        'products': products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)