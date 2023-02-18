from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from .models import Cart, CartItem
from store.models import Product, Variation

# Create your views here.
# underscore indicates a private function
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    product_variation = []
    if request.method == 'POST':
        # get value by name of input option fields:
        for item in request.POST:
            key = item
            value = request.POST[key]
            try:
                variation = Variation.objects.get(product=product, 
                variation_category__iexact=key, 
                variation_value__iexact=value)
                product_variation.append(variation)
            except:
                pass

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request)) # get cart using cart id present in the session
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )
    cart.save()

    cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
    if cart_item_exists:
        cart_item = CartItem.objects.filter(product=product, cart=cart)
        # existing variations -> from database
        # current variation -> product_variation
        # item_id -> from database
        # 1st we check if the current variation is inside the existing variations, because in that
        # case we will increase the quantity of the current item
        existing_variation_list = []
        id = []
        for item in cart_item:
            existing_variations = item.variations.all()
            existing_variation_list.append(list(existing_variations))
            id.append(item.id)

        print(existing_variation_list)

        if product_variation in existing_variation_list:
            # increase cart item quantity
            index = existing_variation_list.index(product_variation)
            item_id = id[index]
            item = CartItem.objects.get(product=product, id=item_id)
            item.quantity += 1
            item.save()
        else:
            item = CartItem.objects.create(product=product, quantity=1, cart=cart)
            # create a new cart item
            if len(product_variation) > 0:
                # first clear variations, so they don't copy on top
                item.variations.clear()
                item.variations.add(*product_variation)
            item.save()
    else:
        cart_item = CartItem.objects.create(
            product = product,
            quantity = 1,
            cart = cart,
        )
        if len(product_variation) > 0:
            cart_item.variations.clear()
            cart_item.variations.add(*product_variation)
        cart_item.save()
    return redirect('cart')

def remove_cart(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')

def remove_cart_item(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

def cart(request, total=0, quantity=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2/100) * total
        grand_total = total + tax
    except Cart.DoesNotExist:
        pass # just ingnore
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/cart.html', context)
    
# def remove_cart_item(request):
#     # grab the cart, delete cart_item: del test_dict['Mani'] del / dict / key  
#     pass
