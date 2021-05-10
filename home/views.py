import os
import re
from datetime import date

import requests
from bs4 import BeautifulSoup
from django.contrib.auth import authenticate, login, logout

from django.core.mail import send_mail
from django.forms import model_to_dict
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
import json
# Create your views here.
from django.views import View

from home.models import ShiliEmail, MaHoaOneTimePad, Database, CrawlPage
from post.models import Post, Comment

from user.models import MyUser, Follower
from django.core.files import File

#
# class Test(View):
#     def get(self, request):
#         today = str(date.today())
#         module_dir = os.path.dirname(__file__)
#         file_path = os.path.join(module_dir, 'stactic/mail/data.txt')
#         with open(file_path) as json_file:
#             data = json.load(json_file)
#         dater = data[len(data) - 1]["today"]
#         if dater != today:
#             Crawl = CrawlPage()
#             data = Crawl.crawNewsData('https://tuoitre.vn', 'https://tuoitre.vn/tin-moi-nhat.htm')
#             data.append({"today":str(today)})
#             with open(file_path, 'w') as outfile:
#                 json.dump(data, outfile)
#         with open(file_path) as json_file:
#             data = json.load(json_file)
#         data = data[:len(data) - 1]
#         return render(request, 'home/lacx.html', {'data': data})


class Index(View):
    def get(self, request):
        if request.user.is_authenticated:
            database = Database()
            kt = database.get_watching(request.user.username)
            if kt:
                return render(request, 'home/home.html', {'page': 'Trang chủ Shili'})
            else:
                return render(request, 'user/all_user.html', {'page': 'all_user'})
        else:
            return render(request, 'home/index.html')


class Login_user(View):
    def post(self, request):
        if request.method == 'POST':
            password = request.POST.get('password')
            username = request.POST.get('username')
            try:
                user = authenticate(username=MyUser.objects.get(email=username), password=password)
            except:
                user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('home:home')
            else:
                err = [
                    'Thông tin đăng nhập không chính xác hoặc tài khoản này chưa được kích hoạt. Vui lòng kiểm tra lại']
                print(username)
                return render(request, 'home/index.html',
                              {'username': username, 'password': password, 'err': err, 'themes': 'login'})


def logout_user(request):
    try:
        logout(request)
    except:
        pass
    return redirect('home:home')


class Register_user(View):
    def post(self, request):
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        new_user = MyUser()
        new_user.first_name = request.POST.get('first_name')
        new_user.last_name = request.POST.get('last_name')
        new_user.username = request.POST.get('username')
        new_user.email = request.POST.get('email')
        new_user.email = request.POST.get('email')
        new_user.birthday = request.POST.get('birthday')
        new_user.gender = request.POST.get('gender')
        password = {'password1': password1, 'password2': password2, }
        err = []
        x = True
        if MyUser.objects.filter(username=new_user.username):
            x = x and False
            err.append('Username này đã tồn tại trong hệ thống, xin thử lại')
        if MyUser.objects.filter(email=new_user.email):
            x = x and False
            err.append('Địa chỉ email đã tồn tại trong hệ thống, Hãy check email khác')
        if not x:
            return render(request, 'home/index.html',
                          {'newuser': new_user, 'password': password, 'themes': 'register',
                           'err': err})
        else:
            email = new_user.email
            new_user.set_password(password1)
            new_user.is_active = 0
            new_user.save()
            one_time_pad = MaHoaOneTimePad()
            result = one_time_pad.ma_hoa(email)
            domain = request.scheme + '://' + request.META['HTTP_HOST']
            url = domain + '/xacthuc/' + result[0] + '/' + result[1]
            content = "We're excited to have you get started. First, you need to confirm your account. Just press the button below."
            theme = ShiliEmail()
            msg_html = theme.form_mail(url, content, email)
            send_mail("Welcome to Shili!", "Hello", "PLC", [email], html_message=msg_html, fail_silently=False)
            err.append('Đăng kí thành công tài khoản. Kiểm tra email để nhận liên kết kích hoạt tài khoản')
            # return render(request, 'home/index.html', {'themes': 'register',  'err': err})
            return redirect('home:test')


class Send_pass(View):
    def post(self, request):
        email = request.POST.get('email')
        if MyUser.objects.filter(email=email).exists():
            one_time_pad = MaHoaOneTimePad()
            result = one_time_pad.ma_hoa(email)
            mail_content = "Hello"
            mail_title = "Shili! Đặt lại mật khẩu"
            domain = request.scheme + '://' + request.META['HTTP_HOST']
            url = domain + '/resetpassword/' + result[0] + '/' + result[1]
            content = "If did not make this request, just ignore this  email. Otherwise, please click the button below to change your password:"
            theme = ShiliEmail()
            msg_html = theme.form_mail(url, content, email, 'xacthuc')
            send_mail(mail_title, mail_content, "PLC", [email], html_message=msg_html, fail_silently=False)
            return HttpResponse('Kiểm tra email để lấy liên kết đến trang thay đổi mật khẩu')
        err = ['Email này không tồn tại trong hệ thống,vui lòng kiểm tra lại']
        return render(request, 'home/index.html', {'email': email, 'themes': 'forgotPass', 'err': err})


class Xac_thuc(View):
    def post(self, request):
        email = request.POST.get('email')
        if MyUser.objects.filter(email=email):
            one_time_pad = MaHoaOneTimePad()
            result = one_time_pad.ma_hoa(email)
            mail_content = "Hello"
            mail_title = "Shili! Xác thực tài khoản"
            domain = request.scheme + '://' + request.META['HTTP_HOST']
            url = domain + '/xacthuc/' + result[0] + '/' + result[1]
            content = "We're excited to have you get started. First, you need to confirm your account. Just press the button below."
            theme = ShiliEmail()
            msg_html = theme.form_mail(url, content, email)
            send_mail(mail_title, mail_content, "PLC", [email], html_message=msg_html, fail_silently=False)
            return render(request, 'home/index.html', {'email': email, 'themes': 'kich_hoat', 'err': [
                'Kiểm tra email để lấy liên kết đến trang xác thực tài khoản']})
        return render(request, 'home/index.html', {'email': email, 'themes': 'kich_hoat', 'err': [
            'Email này không tồn tại trong hệ thống, vui lòng kiểm tra lại']})


class Xacthuc(View):
    def get(self, request, key, ban_ma):
        one_time_pad = MaHoaOneTimePad()
        email = one_time_pad.giai_ma(key, ban_ma)
        context = {
            'email': email,
            'key': key,
            'ban_ma': ban_ma,
        }
        user = MyUser.objects.get(email=email)
        user.is_active = 1
        user.save()
        return render(request, 'mail/xacthuc.html', context)


class ResetPassword(View):
    def get(self, request, key, ban_ma):
        one_time_pad = MaHoaOneTimePad()
        email = one_time_pad.giai_ma(key, ban_ma)
        context = {
            'email': email,
            'key': key,
            'ban_ma': ban_ma,
        }
        return render(request, 'mail/reset_password.html', context)

    def post(self, request, key, ban_ma):
        one_time_pad = MaHoaOneTimePad()
        email = one_time_pad.giai_ma(key, ban_ma)
        mk1 = request.POST.get('password1')
        mk2 = request.POST.get('password2')
        check = {}
        check["mk1"] = mk1
        check["mk2"] = mk2

        x = re.search("^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[a-zA-Z]).{8,}$", mk1)
        if x:
            if mk1 == mk2:
                edit_user = MyUser.objects.get(email=email)
                edit_user.set_password(mk1)
                edit_user.save()
                check["true"] = True
            else:
                check["khopMK"] = False
        else:
            check["domanhMK"] = False
        context = {
            'email': email,
            'key': key,
            'ban_ma': ban_ma,
            'check': check,
        }
        return render(request, 'mail/reset_password.html', context)


class Check(View):
    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        username = data['username']
        email = data['email']
        try:
            MyUser.objects.get(username=username)
            return HttpResponse('Username đã tồn tại trong hệ thống vui lòng thử username mới')
        except:
            pass
        try:
            MyUser.objects.get(email=email)
            return HttpResponse('Địa chỉ email đã tồn tại trong hệ thống, Hãy check email khác')
        except:
            pass
        return HttpResponse('')


class ApiGetContent(View):
    def post(self, request):
        if request.user.is_authenticated:
            a = Follower.objects.filter(main_user=int(request.user.id)).values('followres')
            x = [i["followres"] for i in a] + [request.user.id]
            x = Post.objects.filter(user__id__in=x).exclude(public="Chỉ Mình Tôi").order_by('-created_at')
            out = Database().convert_post(x)
            return JsonResponse(out, safe=False)
        else:
            return redirect('home:home')
