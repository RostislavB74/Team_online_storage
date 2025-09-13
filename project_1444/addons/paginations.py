from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework.response import Response


class PaginationLimitOffset(LimitOffsetPagination):
    default_limit = 4  # змінюй на потрібне значення
    max_limit = 100


class Pagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(
            {
                "links": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "count": self.page.paginator.count,
                "results": data,
            }
        )
