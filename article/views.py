import markdown
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect

from article.form import ArticleForm
from article.models import Article, ArticleColumn
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q

from comments.models import Comment
from userprofile.models import Profile
from PIL import Image
import re


# Create your views here.


def index(request):
    return HttpResponse("Hello, World")


def search_articles(request):
    search = request.GET.get('search')
    order = request.GET.get('order')
    column = request.GET.get('column')
    tag = request.GET.get('tag')


    # 初始化查询集
    article_list = Article.objects.all()

    # 搜索查询集
    if search:
        article_list = article_list.filter(
            Q(title__icontains=search) |
            Q(content__icontains=search)
        )
    else:
        search = ''

    # 栏目查询集
    if column is not None and column.isdigit():
        article_list = article_list.filter(column=column)
    else: column = ''

    # 标签查询集
    if tag and tag != 'None':
        article_list = article_list.filter(tags__name__in=[tag])
    else: tag = ''

    paginator = Paginator(article_list, 5)
    page = request.GET.get('page')
    articles = paginator.get_page(page)

    context = {
        'articles': articles,
        'order': order,
        'search': search,
        'column': column,
        'tag': tag,
    }

    return render(request, 'article/search.html', context)


def article_list(request):
    # 从 url 中提取查询参数
    search = request.GET.get('search')
    order = request.GET.get('order')
    column = request.GET.get('column')
    tag = request.GET.get('tag')

    # 初始化查询集
    article_list = Article.objects.all()

    # 搜索查询集
    if search:
        article_list = article_list.filter(
            Q(title__icontains=search) |
            Q(content__icontains=search)
        )
    else:
        search = ''

    # 栏目查询集
    if column is not None and column.isdigit():
        article_list = article_list.filter(column=column)

    # 标签查询集
    if tag and tag != 'None':
        article_list = article_list.filter(tags__name__in=[tag])

    # 查询集排序
    if order == 'total_views':
        article_list = article_list.order_by('-total_views')

    paginator = Paginator(article_list, 50)
    page = request.GET.get('page')
    articles = paginator.get_page(page)

    # 需要传递给模板（templates）的对象
    context = {
        'articles': articles,
        'order': order,
        'search': search,
        'column': column,
        'tag': tag,
    }

    return render(request, 'article/list.html', context)


def article_detail(request, id):
    article = Article.objects.get(id=id)
    comments = Comment.objects.filter(article=id)
    # 浏览量 +1
    article.total_views += 1
    article.save(update_fields=['total_views'])
    md = markdown.Markdown(
        extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
        ]
    )
    article.content = md.convert(article.content)

    context = {'article': article, 'toc': md.toc, 'comments': comments}

    return render(request, 'article/detail.html', context)


@login_required(login_url='/userprofile/login/')
def article_create(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            new_article = form.save(commit=False)

            new_article.author = User.objects.get(id=request.user.id)
            # 新增的代码
            if request.POST['column'] != 'none':
                new_article.column = ArticleColumn.objects.get(id=request.POST['column'])
            new_article.save()
            form.save_m2m()
            return redirect('article:article_list')
        else:
            return HttpResponse("Error")
    else:
        form = ArticleForm()
        columns = ArticleColumn.objects.all()
        context = {'form': form, 'columns': columns}
        return render(request, 'article/create.html', context)


def article_delete(request, id):
    article = Article.objects.get(id=id)
    article.delete()
    return redirect('article:article_list')


def article_safe_delete(request, id):
    if request.method == 'POST':
        article = Article.objects.get(id=id)
        article.delete()
        return redirect('article:article_list')
    else:
        return HttpResponse("POST ONLY")


@login_required(login_url='/userprofile/login/')
def update_article(request, id):
    article = Article.objects.get(id=id)
    if request.user != article.author:
        return HttpResponse("抱歉，你无权修改这篇文章。")
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article.title = request.POST['title']
            article.content = request.POST['content']
            # 新增的代码
            if request.POST['column'] != 'none':
                article.column = ArticleColumn.objects.get(id=request.POST['column'])
            else:
                article.column = None
            if request.FILES.get('avatar'):
                article.avatar = request.FILES.get('avatar')

                # 修改的部分
            tags_str = request.POST.get('tags')
            # 使用逗号作为分隔符来拆分标签字符串
            tags_list = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
            # 设置标签
            article.tags.set(tags_list, clear=True)
            article.save()
            return redirect('article:article_detail', id=id)
        else:
            return HttpResponse("Error")
    else:
        form = ArticleForm()
        # 新增及修改的代码
        columns = ArticleColumn.objects.all()
        context = {
            'article': article,
            'article_post_form': form,
            'columns': columns,
            'tags': ','.join([x for x in article.tags.names()]),
        }
        return render(request, 'article/update.html', context)
