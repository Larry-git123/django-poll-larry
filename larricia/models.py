import time, uuid

from django.db import models

# Create your models here.

# 用uuid生成文章id
def next_id():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)
    
class Blog(models.Model):
    id = models.CharField(primary_key=True, default=next_id, max_length=50)
    user_id = models.CharField('用户id', max_length=50)
    user_name = models.CharField('用户名', max_length=50)
    user_image = models.CharField('图片路径', max_length=500)
    name = models.CharField('标题', max_length=50)
    summary = models.CharField('摘要', max_length=200)
    content = models.TextField('内容')
    created_at = models.FloatField(default=time.time)
    
class Comment(models.Model):
    id = models.CharField(primary_key=True, default=next_id, max_length=50)
    blog_id = models.CharField('博文id', max_length=50)
    user_id = models.CharField('用户id', max_length=50)
    user_name = models.CharField('用户名', max_length=50)
    content = models.TextField('内容')
    created_at = models.FloatField(default=time.time)