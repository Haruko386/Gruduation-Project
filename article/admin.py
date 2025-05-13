from django.contrib import admin

from .models import Article
from .models import ArticleColumn

# Register your models here.

admin.site.register(Article)

# 注册文章栏目
admin.site.register(ArticleColumn)
