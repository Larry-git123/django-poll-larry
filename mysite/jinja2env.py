# 初始化jinja2环境
'''
    示例：
    <img src="{{ static('path/to/my_picture.png') }}">
    <a href="{{ url('namespace:url_name', args=(some_arg,)) }}">Some link</a>
'''
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse

from jinja2 import Environment

from larricia.datetime_filter import datetime_filter

def environment(**options):
    env = Environment(**options)
    # jinja2下使用static和url tag
    env.globals.update({
        'static': staticfiles_storage.url,
        'url': reverse,
    })
    # 设置自定义日期过滤器
    env.filters['datetime'] = datetime_filter
    return env