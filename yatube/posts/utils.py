from django.core.paginator import Paginator


def paginate(request, obj, amount):
    paginator = Paginator(obj, amount)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
