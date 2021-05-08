import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.views import View
from home.models import Database
from user.models import Follower, MyUser


class Profile(View):
    def get(self, request, user_username):
        if request.user.is_authenticated:
            if request.user.username == user_username:
                return redirect('user:profile_main')
            return render(request, 'user/profile.html', {'username': user_username, 'page': 'profile'})
        else:
            return redirect('home:home')


class ProfileMain(View):
    def get(self, request):
        if request.user.is_authenticated:
            return render(request, 'user/profile.html', {'username': request.user.username, 'page': 'profile'})
        else:
            return redirect('home:home')


class ApiGetProfile(View):
    def post(self, request):
        if request.user.is_authenticated:
            data = json.loads(request.body.decode('utf-8'))
            database = Database()
            profile = database.get_profile(data['username'])
            profile_posts = database.get_profile_posts(data['username'], request.user.username)
            profile_watching = database.get_watching(data['username'])
            profile_followed = database.get_followed(data['username'])
            return JsonResponse(
                {'profile': profile, 'profile_posts': profile_posts, 'dangtheodoi': profile_watching,
                 'duoctheodoi': profile_followed})
        else:
            return redirect('home:home')


class ApiEditProfile(View):
    def post(self, request):
        if request.user.is_authenticated:

            edit_user = MyUser.objects.get(id=request.user.id)

            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            address = request.POST.get('address')
            email = request.POST.get('email')
            gender = request.POST.get('gender')
            birthday = request.POST.get('birthday')
            intro = request.POST.get('intro')
            if first_name != '' and last_name != '':
                edit_user.first_name = first_name
                edit_user.last_name = last_name
            if address != '':
                edit_user.address = address
            if email != '':
                edit_user.email = email
            if gender != edit_user.gender:
                edit_user.gender = gender
            if birthday != edit_user.birthday:
                edit_user.birthday = birthday
            edit_user.intro = intro
            edit_user.save()
            return redirect('user:profile_main')
        else:
            return redirect('home:home')


class Edit_av_bg(View):
    def post(self, request):
        if request.user.is_authenticated:
            edit_user = MyUser.objects.get(id=request.user.id)
            try:
                edit_user.avatar = request.FILES['new_avatar']
                edit_user.save()
            except:
                pass
            try:
                edit_user.cover_image = request.FILES['new_cover_image']
                edit_user.save()
            except:
                pass
            return redirect('user:profile_main')
        else:
            return redirect('home:login')


class Add_follow(View):
    def post(self, request):
        if request.user.is_authenticated:
            data = json.loads(request.body.decode('utf-8'))
            x = Follower.objects.filter(main_user=request.user, followres=data['id'])
            if not x:
                fl = Follower()
                fl.main_user = request.user
                fl.followres = MyUser.objects.get(id=data['id'])
                fl.save()
                return HttpResponse('Follow thành công, hãy tiếp tục theo dõi những người khác')
            else:
                fl = Follower.objects.get(f_id=x[0].f_id)
                fl.delete()
                return HttpResponse('Hủy follow thành công, hãy tiếp tục theo dõi những người khác')
        else:
            return HttpResponse('Phiên đăng nhập đã hết hạn.')


class AllUser(View):
    def get(self, request):
        if request.user.is_authenticated:
            return render(request, 'user/all_user.html', {'page': 'all_user'})
        else:
            return redirect('home:home')

    def post(self, request):
        if request.user.is_authenticated:
            data = Follower.objects.filter(main_user=request.user).values('followres_id')
            x = [i["followres_id"] for i in data]
            all_user = MyUser.objects.all().exclude(id__in=[request.user.id] + x).values('id', 'username', 'avatar', 'first_name', 'last_name')
            all_user = [i for i in all_user]
            return JsonResponse({'result': all_user})
        else:
            return redirect('home:home')


class ApiYourFriend(View):
    def post(self, request):
        if request.user.is_authenticated:
            database = Database()
            profile_watching = database.get_watching(request.user.username)
            return JsonResponse({'result': profile_watching})
        else:
            return JsonResponse({'result': []})
