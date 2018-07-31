from django.urls import path

from . import views

app_name = 'larricia'
urlpatterns = [
    # 首页
    path('', views.index, name='index'),
    # 获取用户列表
    path('api/users/', views.api_get_users, name='api_get_users'),
    # 注册
    path('register/', views.manage_register, name='register'),
    path('api/newuser/', views.api_register_user, name='api_register_user'),
    # 登录
    path('signin/', views.manage_signin, name='signin'),
    path('api/authenticate/', views.api_signin_user, name='authenticate'),
    # 登出
    path('api/signout/', views.api_signout_user, name='api_signout_user'),
    # 创建日志
    path('manage/blogs/create/', views.manage_create_blog, name='manage_create_blog'),
    path('api/newblog/', views.api_edit_blog, name='api_create_blog'),
    # 获取日志
    path('blog/', views.get_blog, name='get_blog'), # 供渲染用
    path('blog/<str:id>/', views.get_blog),
    path('api/blogs/', views.api_blogs, name='api_blogs'),
    # 编辑日志
    path('manage/blogs/edit/', views.manage_edit_blog, name='manage_edit_blog'),
    path('manage/blogs/edit/<str:id>/', views.manage_edit_blog),
    path('api/blog/', views.api_get_blog, name='api_get_blog'),
    path('api/blog/<str:id>/', views.api_get_blog),
    path('api/editblog/<str:id>/', views.api_edit_blog, name='api_edit_blog'),
    # 删除日志
    path('api/deleteblog/', views.api_delete_blog, name='api_delete_blog'),
    path('manage/blogs/', views.manage_blogs, name='manage_blogs'),
]