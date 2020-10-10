# encoding:utf-8
from rest_framework.response import Response


class APIResponse(Response):
    def __init__(self, result=None, status="ok", msg="", http_status=None,
                 code=200, headers=None, exception=False, **kwargs):
        data = {
            "status": status,
            "message": msg,
            "result": result,
            "code": code
        }
        if kwargs:
            data.update(kwargs)
        super().__init__(data=data, status=http_status, headers=headers, exception=exception)
