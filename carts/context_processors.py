# takes a request as the argument and returns a dictionary of data
from .models import Cart, CartItem
from .views import _cart_id

def counter(request):
    cart_count = 0
    # do nothing if admin:
    if 'admin' in request.path:
        return {}
    # counts the CartItems; we fetch the cart via session id
    else:
        try:
            cart = Cart.objects.filter(cart_id=_cart_id(request))
            # colon denotes slice
            cart_items = CartItem.objects.all().filter(cart=cart[:1])
            for item in cart_items:
                cart_count += item.quantity
        except:
            if Cart.DoesNotExist:
                cart_count = 0
    return dict(cart_count=cart_count)
