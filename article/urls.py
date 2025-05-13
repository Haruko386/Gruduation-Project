from django.urls import path

from article import views

app_name = 'article'

urlpatterns = [
    # path('', views.index, name='index'),
    path('', views.article_list, name='article_list'),
    path('article-detail/<int:id>/', views.article_detail, name='article_detail'),
    path('article-create/', views.article_create, name='article_create'),
    path('article-delete/<int:id>/', views.article_delete, name='article_delete'),
    path('article-safe-delete/<int:id>', views.article_safe_delete, name='article_safe_delete'),
    path('article-update/<int:id>/', views.update_article, name='article_update'),
    path('search/', views.search_articles, name='search_articles'),
]
