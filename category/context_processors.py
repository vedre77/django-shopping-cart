# takes a request as the argument and returns a dictionary of data
from .models import Category 

def menu_links(request):
    # fetch all categories from the database
    links = Category.objects.all()
    return dict(links=links)
