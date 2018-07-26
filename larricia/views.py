import re, time

from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.http import HttpResponse, JsonResponse

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
    blogs = get_list_or_404(Blog)
    context = { 'blogs': blogs }
    return render(request, 'larricia/blogs.html', context)
    
def api_get_users(request):
    users = get_list_or_404(User)
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

def manage_create_blog():
    context = {
        'id': '',
        'action': 'larricia:api_create_blog'
    }
    return render(reuqest, 'larricia/manage_blog_edit.html', context)
    
# 日志创建
def api_create_blog(request, *, name, summary, content):
    # check_admin(request)
    if not name or not name.strip():
        raise FieldError('name empty')
    if not summary or not summary.strip():
        raise FieldError('summary empty')
    if not content or not content.strip():
        raise FieldError('content empty')
    blog = Blog(user_id=request.__user__.id, user_name=request.__user__.name, user_image=request.__user__.image, name=name.strip(), summary=summary.strip(), content=content.strip())
    blog.save()
    return blog

# 日志查看
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
def api_blogs(request, *, pages='1'):
    page_index = get_page_index(pages)
    num = User.objects.count()
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, blogs=())
    blogs = User.objects.order_by('-created_at')[p.offset:p.offset+p.limit]
    return JsonResponse(dict(page=p, blogs=blogs), default=lambda obj: obj.__dict__)
    
def api_get_blog(request, *, id):
    blog = get_object_or_404(Blog, id=id)
    return blog
    
# 管理页面
def manage_blogs(request, *, page='1'):
    return render(request, 'larricia/manage_blog.html', {'page_index': get_page_index(page)})