from django.urls import path

from . import views

app_name = 'larricia'
urlpatterns = [
    path('', views.index, name='index'),
    path('api/users/', views.api_get_users, name='api_get_users'),
    path('api/newuser/', views.api_register_user, name='api_register_user'),
    path('api/authenticate/', views.authenticate, name='authenticate'),
    path('manage/blogs/create/', views.manage_create_blog, name='manage_create_blog'),
    path('api/newblog/', views.api_create_blog, name='api_create_blog'),
    path('blog/<str:id>/', views.get_blog, name='get_blog'),
    path('api/blogs/', views.api_blogs, name='api_blogs'),
    path('api/blogs/<str:id>/', views.api_get_blog, name='api_get_blog'),
    path('manage/blogs/', views.manage_blogs, name='manage_blogs'),
]