from django.contrib import admin
from .models import Choice, Question
# Register your models here.

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3
    
class QuestionAdmin(admin.ModelAdmin):
    # fields = ['pub_date', 'question_text']
    fieldsets = [
        (None, {'fields': ['question_text']}),
        ('时间信息', {'fields': ['pub_date'], 'classes': ['collapse']}),
    ]
    inlines = [ChoiceInline]
    # make some tweaks to the “change list” page
    list_display = ('question_text', 'pub_date', 'was_published_recently')
    # filters using the list_filter
    list_filter = ['pub_date']
    # add some search capability
    search_fields = ['question_text']
    
admin.site.register(Question, QuestionAdmin)
# admin.site.register(Choice)