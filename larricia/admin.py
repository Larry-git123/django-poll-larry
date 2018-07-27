from django.contrib import admin

from .models import Blog, User
# Register your models here.
class BlogAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name']}),
        ('文章信息', {'fields': ['summary', 'content']}),
        ('用户信息', {'fields': ['user_id', 'user_name', 'user_image']}),
    ]
    # make some tweaks to the “change list” page
    list_display = ('name', 'summary')
    # add some search capability
    search_fields = ['name']
    
admin.site.register(Blog, BlogAdmin)
    
admin.site.register(User)