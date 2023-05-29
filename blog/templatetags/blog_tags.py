from django.db.models import Count
from django import template
from blog.models import *


register = template.Library()


@register.inclusion_tag('blog/list_categories.html')
def show_categories(sort=None, cat_selected=0):
    if not sort:
        cats = Category.objects.all()
        # cats = Blog.cat.objects.all()

    else:
        cats = Category.objects.order_by(sort)
        # cats = Blog.cat.objects.order_by(sort)
        # cats = Category.objects.annotate(Count('blog'))

    return {'cats': cats, 'cat_selected': cat_selected}
