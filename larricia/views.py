import re, time, json

from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.http import HttpResponse, JsonResponse
from django.urls import reverse

from .models import User, Blog, Comment, next_id
from .cookieutils import user2cookie, COOKIE_NAME
from .page import Page, get_page_index

from . import markdown2

# Create your views here.
_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')

def text2html(text):
    lines = map(lambda s: '<p>%s</p>' % s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'), filter(lambda s: s.strip() != '', text.split('\n')))
    return ''.join(lines)
    
def index(request):
    # users = get_list_or_404(User)
    blogs = get_list_or_404(Blog.objects.order_by('-created_at')[0:10])
    context = { 'blogs': blogs }
    return render(request, 'larricia/blogs.html', context)
    
def api_get_users(request):
    users = get_list_or_404(User)
    print('USERS:', users)
    # 隐藏密码
    for u in users:
        u.passwd = '******'
    context = { 'users': users }
    return JsonResponse(context, json_dumps_params={'default': lambda obj: obj.__dict__})
    
# 用户注册
def api_register_user(request, *, email, name, passwd):
    if not name or not name.strip():
        raise FieldError('name')
    if not email or not _RE_EMAIL.match(email):
        raise ValidationError('email')
    if not passwd or not _RE_SHA1.match(passwd):
        raise ValidationError('passwd')
    users = get_list_or_404(User, email=email)
    if len(users) > 0:
        raise ValidationError('Email is already in use.')
    uid = next_id()
    sha1_passwd = '%s:%s' % (uid, passwd)
    user = User(id=uid, name=name.strip(), email=email, passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(), image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest())
    user.save()
    r = HttpResponse()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.content = json.dumps(user, default=lambda obj: obj.__dict__, ensure_ascii=False).encode('utf-8')
    return r
    
# 用户登录
def authenticate(request, *, email, passwd):
    if not email or not _RE_EMAIL.match(email):
        raise ValidationError('email')
    if not passwd or not _RE_SHA1.match(passwd):
        raise ValidationError('passwd')
    users = get_list_or_404(User, email=email)
    if len(users) == 0:
        raise ValidationError('Email not exist.')
    user = user[0]
    # 检查密码
    sha1 = hashlib.sha1()
    sha1.update(user.id.encode('utf-8'))
    sha1.update(b':')
    sha1.update(passwd.encode('utf-8'))
    if passwd != sha1.hexdigest():
        raise ValidationError('Invalid Password.')
    # 认证成功，创建Cookie
    r = HttpResponse()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.content = json.dumps(user, default=lambda obj: obj.__dict__, ensure_ascii=False).encode('utf-8')
    return r

# 日志管理页面
def manage_blogs(request):
    page = request.GET.get('page', '1')
    return render(request, 'larricia/manage_blog.html', {'page_index': get_page_index(page)})
    
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
    if len(kw) != 0:
        # 为减少数据库查询，直接使用现有id创建新对象存入数据库
        blog = Blog(id=kw['id'], user_id='1212', user_name='Larry Liu', user_image='about:blank', name=name.strip(), summary=summary.strip(), content=content.strip())
    else:
        blog = Blog(user_id='1212', user_name='Larry Liu', user_image='about:blank', name=name.strip(), summary=summary.strip(), content=content.strip())
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