from rest_framework.pagination import LimitOffsetPagination


class Pagination(LimitOffsetPagination):
    default_limit = 4  # змінюй на потрібне значення
    max_limit = 100
