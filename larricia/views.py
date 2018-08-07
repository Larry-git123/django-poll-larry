import re, time, json

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.http import HttpResponse, JsonResponse
from django.urls import reverse

from .models import Blog, Comment, next_id
from .cookieutils import user2cookie, COOKIE_NAME
from .page import Page, get_page_index

from . import markdown2

# Create your views here.
_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')

def text2html(text):
    lines = map(lambda s: '<p>%s</p>' % s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'), filter(lambda s: s.strip() != '', text.split('\n')))
    return ''.join(lines)
    
# 返回JSON错误信息
def jsonfail(message):
    return JsonResponse({ 'error': 'http_bad_response', 'data': '500', 'message': message })

def index(request):
    blogs = get_list_or_404(Blog.objects.order_by('-created_at')[0:10])
    context = { 'blogs': blogs, 'user': request.user }
    return render(request, 'larricia/blogs.html', context)
    
def api_get_users(request):
    users = get_list_or_404(User)
    print('USERS:', users)
    # 隐藏密码
    for u in users:
        u.passwd = '******'
    context = { 'users': users }
    return JsonResponse(context, json_dumps_params={'default': lambda obj: obj.__dict__})

def manage_register(request):
    return render(request, 'larricia/register.html')
    
# 用户注册
def api_register_user(request):
    data = json.loads(request.body)
    name = data['name']
    email = data['email']
    passwd = data['passwd']
    print('PASSWD:', passwd)
    if not name or not name.strip():
        return jsonfail('请输入用户名test')
    if not email or not _RE_EMAIL.match(email):
        return JsonResponse({ 'error': 'http_bad_response', 'data': '500', 'message': '电子邮件格式不正确' })
    if not passwd or not _RE_SHA1.match(passwd):
        return JsonResponse({ 'error': 'http_bad_response', 'data': '500', 'message': '密码格式不正确' })
    # 这里不能用get_list_or_404，因为该函数在查询到的列表为空时会直接抛出Http404异常，从而无法根据列表是否为空作进一步判断
    # 应该调用Foo.objects.filter方法返回QuerySet，然后用len判断
    if len(User.objects.filter(email=email)) > 0:
        return jsonfail('电子邮件已被使用')
    uid = next_id()
    sha1_passwd = '%s:%s' % (uid, passwd)
    # 创建用户并保存
    user = User.objects.create_user(name, email, passwd)
    # 自动登录
    login(request, user, backend='larricia.backend.EmailBackend')
    return JsonResponse({ 'username': name, 'email': email })

def manage_signin(request):
    return render(request, 'larricia/signin.html')
    
# 用户登录
def api_signin_user(request):
    data = json.loads(request.body)
    email = data['email']
    passwd = data['passwd']
    if not email or not _RE_EMAIL.match(email):
        return JsonResponse({ 'error': 'http_bad_response', 'data': '500', 'message': '电子邮件格式不正确' })
    if not passwd or not _RE_SHA1.match(passwd):
        return JsonResponse({ 'error': 'http_bad_response', 'data': '500', 'message': '密码不正确' })
    # 进行用户认证
    user = authenticate(email=email, password=passwd)
    if user is not None and user.is_active:
    # 认证成功，登录用户
        login(request, user)
        context = { 'email': email }
    else:
    # 认证失败
        context = { 'error': 'http_bad_response', 'data': '500', 'message': '登录失败，请确认电子邮件和密码' }
    return JsonResponse(context)

# 用户登出
def api_signout_user(request):
    logout(request)
    return index(request)
    
# 日志管理页面
def manage_blogs(request):
    page = request.GET.get('page', '1')
    context = {'page_index': get_page_index(page), 'user': request.user }
    return render(request, 'larricia/manage_blog.html', context)
    
# 转到创建新日志页面
def manage_create_blog(request):
    context = {
        'id': '',
        'action': reverse('larricia:api_create_blog')
    }
    return render(request, 'larricia/manage_blog_edit.html', context)
    
# 转到编辑已有日志页面
def manage_edit_blog(request, id):
    context = {
        'id': id,
        'action': reverse('larricia:api_edit_blog', args=(id,))
    }
    return render(request, 'larricia/manage_blog_edit.html', context)

# 获取日志以编辑    
def api_get_blog(request, id):
    blog = get_object_or_404(Blog, id=id)
    return JsonResponse(blog.__dict__, json_dumps_params={'default': lambda obj: obj.__dict__})
    
# 创建/编辑日志
def api_edit_blog(request, **kw):
    # request.POST针对form方式提交的内容。通过ajax提交的内容在request.body里。
    data = json.loads(request.body)
    name = data['name']
    summary = data['summary']
    content = data['content']
    # check_admin(request)
    if not name or not name.strip():
        raise FieldError('name empty')
    if not summary or not summary.strip():
        raise FieldError('summary empty')
    if not content or not content.strip():
        raise FieldError('content empty')
    user = request.user
    if len(kw) != 0:
        # 为减少数据库查询，直接使用现有id创建新对象存入数据库
        blog = Blog(id=kw['id'], user_id=user.id, user_name=user.username, user_image='http://www.gravatar.com/avatar/%s?d=mm&s=120', name=name.strip(), summary=summary.strip(), content=content.strip())
    else:
        blog = Blog(user_id=user.id, user_name=user.username, user_image='http://www.gravatar.com/avatar/%s?d=mm&s=120', name=name.strip(), summary=summary.strip(), content=content.strip())
    blog.save()
    # 构建JSON并返回
    return JsonResponse(blog.__dict__, json_dumps_params={'default': lambda obj: obj.__dict__})
    # return redirect(reverse('larricia:get_blog', args=(blog.id,)))

# 日志阅读
def get_blog(request, id):
    blog = get_object_or_404(Blog, id=id)
    comments = Comment.objects.filter(blog_id=id).order_by('-created_at')
    for c in comments:
        c.html_content = text2html(c.content)
    blog.html_content = markdown2.markdown(blog.content)
    context = {
        'blog': blog,
        'comments': comments
    }
    return render(request, 'larricia/blog.html', context)

# 日志列表
def api_blogs(request):
    pages = request.GET.get('page', '1')
    page_index = get_page_index(pages)
    num = Blog.objects.count()
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, blogs=())
    '''
        注意，filter和order_by方法返回的是QuerySet类型，不能被序列化为JSON
        get_list_or_404方法在内部对QuerySet调用了list()方法，因此其返回值可通过转化为__dict__序列化为JSON
    '''
    blogs = get_list_or_404(Blog.objects.order_by('-created_at')[p.offset:p.offset+p.limit])
    context = {'page': p, 'blogs': blogs}
    return JsonResponse(context, json_dumps_params={'default': lambda obj: obj.__dict__})
    
# 删除日志
def api_delete_blog(request):
    id = json.loads(request.body)['id']
    blog = get_object_or_404(Blog, id=id)
    # delete()返回一个由删除元素个数和包含每种对象删除数的dict的tuple
    return JsonResponse(blog.delete()[1])
    
# 发表评论
def api_post_comment(request, id):
    # 获取当前用户信息
    user = request.user
    # 获取评论内容
    content = json.loads(request.body).get('content', '')
    comment = Comment(blog_id=id, user_id=user.id, user_name=user.username, content=content)
    comment.save()
    return JsonResponse({'comment_id': comment.id })