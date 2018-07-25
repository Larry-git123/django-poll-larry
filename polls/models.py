import datetime

from django.db import models
from django.utils import timezone

# Create your models here.
class Question(models.Model):
    question_text = models.CharField(max_length=200, verbose_name='问题文本')
    pub_date = models.DateTimeField('发布时间')
    
    def __str__(self):
        return self.question_text
        
    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now
    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = '最近发布?'
    
    class Meta:
        verbose_name = '问题'
        verbose_name_plural = verbose_name
    
class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200, verbose_name='选项文本')
    votes = models.IntegerField(default=0, verbose_name='票数')
    
    def __str__(self):
        return self.choice_text
        
    class Meta:
        verbose_name = '选项'
        verbose_name_plural = verbose_name