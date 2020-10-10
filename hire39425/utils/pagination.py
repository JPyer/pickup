from rest_framework.pagination import PageNumberPagination

from utils.response import APIResponse


class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'pageSize'
    page_query_param = "pageNo"
    # url参数
    max_page_size = 100

    def get_paginated_response(self, data):
        return APIResponse(
            code=200,
            data=data,
            totalCount=self.page.paginator.count, current=self.page.number, pageNo=self.page.number,
            pageSize=self.page_size, totalPage=self.page.paginator.num_pages,
            next=self.get_next_link(), previous=self.get_previous_link(),

        )
