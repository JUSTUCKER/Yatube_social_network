from http import HTTPStatus

from django.shortcuts import redirect, render


def page_not_found(request, exception):
    return render(
        request,
        'core/404.html',
        {'path': request.path},
        status=HTTPStatus.NOT_FOUND
    )


def csrf_failure(request, reason=''):
    return redirect('core/403csrf.html')
