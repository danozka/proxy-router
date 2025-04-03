from enum import StrEnum


class RequestMethod(StrEnum):
    connect = 'CONNECT'
    delete = 'DELETE'
    get = 'GET'
    head = 'HEAD'
    options = 'OPTIONS'
    patch = 'PATCH'
    post = 'POST'
    put = 'PUT'
    trace = 'TRACE'
