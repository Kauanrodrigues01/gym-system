from django.test import TestCase
from django.core.exceptions import ValidationError
from django.http import HttpRequest
from utils.utils import verify_email, is_valid_cpf, make_pagination, make_pagination_range
from django.core.paginator import Paginator
from faker import Faker

faker = Faker('pt_BR')


class UtilsTestCase(TestCase):
    def test_verify_email_valid(self):
        self.assertTrue(verify_email('test@example.com'))

    def test_verify_email_invalid(self):
        self.assertFalse(verify_email('invalid-email'))

    def test_is_valid_cpf_valid(self):
        self.assertTrue(is_valid_cpf(faker.cpf().replace('.', '').replace('-', '')))
        
    def test_is_valid_cpf_invalid_first_digit(self):
        self.assertFalse(is_valid_cpf('12345678919')) 

    def test_is_valid_cpf_invalid(self):
        self.assertFalse(is_valid_cpf('12345678900'))

    def test_make_pagination_range(self):
        page_range = range(1, 21)  # Pages 1 to 20
        current_page = 5
        qty_pages = 6

        expected = [3, 4, 5, 6, 7, 8]
        result = make_pagination_range(page_range, qty_pages, current_page)
        self.assertEqual(list(result['pagination']), expected)  # Converte para lista


    def test_make_pagination(self):
        # Mock a queryset
        class MockQuerySet:
            def __getitem__(self, item):
                return list(range(1, 101))[item]

            def __len__(self):
                return 100

        queryset = MockQuerySet()
        request = HttpRequest()
        request.GET['page'] = '3'  # Page 3

        per_page = 10
        qty_pages = 6
        page_obj, pagination_range = make_pagination(request, queryset, per_page, qty_pages)

        self.assertEqual(page_obj.number, 3)
        self.assertEqual(list(page_obj.object_list), list(range(21, 31)))
        self.assertEqual(list(pagination_range['pagination']), [1, 2, 3, 4, 5, 6])


    def test_make_pagination_invalid_page(self):
        # Mock a queryset
        class MockQuerySet:
            def __getitem__(self, item):
                return list(range(1, 101))[item]

            def __len__(self):
                return 100

        queryset = MockQuerySet()
        request = HttpRequest()
        request.GET['page'] = 'invalid'  # Invalid page input

        per_page = 10
        qty_pages = 5
        page_obj, pagination_range = make_pagination(request, queryset, per_page, qty_pages)

        self.assertEqual(page_obj.number, 1)  # Defaults to page 1
        self.assertEqual(list(page_obj.object_list), list(range(1, 11)))
        
        
    def test_make_pagination_range_stop_range_exceeds_total_pages(self):
        page_range = range(1, 21)  # Pages 1 to 20
        current_page = 19  # Near the end of page range
        qty_pages = 6  # Large qty_pages to exceed range
        
        expected = [15, 16, 17, 18, 19, 20]  # Adjusted range
        result = make_pagination_range(page_range, qty_pages, current_page)
        self.assertEqual(list(result['pagination']), expected)

