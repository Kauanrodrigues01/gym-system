from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.mail import EmailMessage

def send_email(subject, message, to_email):
    email = EmailMessage(
        subject=subject,
        body=message,
        to=[to_email]
    )
    email.send()

def verify_email(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False

def is_valid_cpf(cpf):
    """Valida o CPF usando o algoritmo dos dígitos verificadores."""

    cpf = [int(digit) for digit in cpf]

    sum_1 = sum(cpf[i] * (10 - i) for i in range(9))
    digit_1 = (sum_1 * 10 % 11) % 10
    if digit_1 != cpf[9]:
        # COVERAGE ESTÁ DIZENDO QUE NÃO TESTEI ESSA POSSIBILIDADE
        return False

    sum_2 = sum(cpf[i] * (11 - i) for i in range(10))
    digit_2 = (sum_2 * 10 % 11) % 10
    if digit_2 != cpf[10]:
        return False

    return True

import math

from django.core.paginator import Paginator


def make_pagination_range(
    page_range,
    qty_pages,
    current_page,
):
    middle_range = math.ceil(qty_pages / 2)
    start_range = current_page - middle_range
    stop_range = current_page + middle_range
    total_pages = len(page_range)

    start_range_offset = abs(start_range) if start_range < 0 else 0

    if start_range < 0:
        start_range = 0
        stop_range += start_range_offset

    if stop_range >= total_pages:
        # COVERAGE ESTÁ DIZENDO QUE NÃO TESTEI ESSA POSSIBILIDADE
        start_range = start_range - abs(total_pages - stop_range)

    pagination = page_range[start_range:stop_range]
    return {
        'pagination': pagination,
        'page_range': page_range,
        'qty_pages': qty_pages,
        'current_page': current_page,
        'total_pages': total_pages,
        'start_range': start_range,
        'stop_range': stop_range,
        'first_page_out_of_range': current_page > middle_range,
        'last_page_out_of_range': stop_range < total_pages,
    }


def make_pagination(request, queryset, per_page, qty_pages=4):
    try:
        current_page = int(request.GET.get('page', 1))
    except ValueError:
        current_page = 1

    paginator = Paginator(queryset, per_page)
    page_obj = paginator.get_page(current_page)

    pagination_range = make_pagination_range(
        paginator.page_range,
        qty_pages,
        current_page
    )

    return page_obj, pagination_range