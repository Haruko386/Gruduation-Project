from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from .forms import UserLoginForm
from .forms import UserLoginForm, UserRegisterForm
from .forms import ProfileForm
from .models import Profile
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


# Create your views here.

def user_login(request):
    if request.method == 'POST':
        user_login_form = UserLoginForm(data=request.POST)
        if user_login_form.is_valid():
            data = user_login_form.cleaned_data
            user = authenticate(username=data['username'], password=data['password'])
            if user:
                login(request, user)
                return redirect("article:article_list")
            else:
                messages.error(request, "用户名或密码不正确")
                return render(request, 'userprofile/login.html', {'form': user_login_form})
        else:
            messages.error(request, "表单数据无效")
            return render(request, 'userprofile/login.html', {'form': user_login_form})
    elif request.method == 'GET':
        user_login_form = UserLoginForm()
        return render(request, 'userprofile/login.html', {'form': user_login_form})
    else:
        messages.error(request, "无效的请求方法")
        return render(request, 'userprofile/login.html')


def user_logout(request):
    logout(request)
    return redirect("article:article_list")


# 引入 UserRegisterForm 表单类
from .forms import UserLoginForm, UserRegisterForm


# 用户注册
from django.contrib import messages

def user_register(request):
    if request.method == 'POST':
        user_register_form = UserRegisterForm(data=request.POST)
        if user_register_form.is_valid():
            new_user = user_register_form.save(commit=False)
            new_user.set_password(user_register_form.cleaned_data['password'])
            new_user.save()
            login(request, new_user)
            return redirect("article:article_list")
        else:
            for error in user_register_form.errors.values():
                messages.error(request, error)
            return render(request, 'userprofile/register.html', {'form': user_register_form})
    elif request.method == 'GET':
        user_register_form = UserRegisterForm()
        context = {'form': user_register_form}
        return render(request, 'userprofile/register.html', context)
    else:
        messages.error(request, "无效的请求方法")
        return render(request, 'userprofile/register.html')



@login_required(login_url='/userprofile/login/')
def user_delete(request, id):
    if request.method == 'POST':
        user = User.objects.get(id=id)
        # 验证登录用户、待删除用户是否相同
        if request.user == user:
            # 退出登录，删除数据并返回博客列表
            logout(request)
            user.delete()
            return redirect("article:article_list")
        else:
            return HttpResponse("你没有删除操作的权限。")
    else:
        return render(request, 'userprofile/error.html')


@login_required(login_url='/userprofile/login/')
def profile_edit(request, id):
    user = User.objects.get(id=id)
    # user_id 是 OneToOneField 自动生成的字段
    profile = Profile.objects.get(user_id=id)

    if request.method == 'POST':
        # 验证修改数据者，是否为用户本人
        if request.user != user:
            return HttpResponse("你没有权限修改此用户信息。")

        profile_form = ProfileForm(request.POST, request.FILES)
        if profile_form.is_valid():
            profile_cd = profile_form.cleaned_data
            profile.phone = profile_cd['phone']
            profile.bio = profile_cd['bio']
            if 'avatar' in request.FILES:
                profile.avatar = profile_cd["avatar"]
            profile.save()
            return redirect("userprofile:edit", id=id)
        else:
            return render(request, 'userprofile/error.html')

    elif request.method == 'GET':
        profile_form = ProfileForm()
        context = {'profile_form': profile_form, 'profile': profile, 'user': user}
        return render(request, 'userprofile/edit.html', context)
    else:
        return render(request, 'userprofile/error.html')


