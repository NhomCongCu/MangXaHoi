from django.db.models import Count
from django.forms import model_to_dict
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
import json
# Create your views here.
from django.views import View

from home.models import Database
from post.models import Comment, Post


class ShowPost(View):
    def get(self, request, post_id):
        if request.user.is_authenticated:
            return render(request, 'home/home.html', {'post_id': post_id, 'page': 'Bài viết với ID là'})
        else:
            return redirect('home:home')

    def post(self, request, post_id):
        if request.user.is_authenticated:
            x = Post.objects.filter(post=post_id)
            result = Database().convert_post(x)
            return JsonResponse(result, safe=False)
        else:
            return redirect('home:login')


class TopHashtagPost(View):
    def get(self, request):
        if request.user.is_authenticated:
            return render(request, 'home/home.html', {'page': 'Các bài viết nổi bật trong tuần'})
        else:
            return redirect('home:home')

    def post(self, request):
        if request.user.is_authenticated:
            database = Database()
            x = list(Post.objects.all().values('hashtag').annotate(soluot=Count('hashtag')).order_by('-soluot'))[:3]
            list_ht = [i["hashtag"] for i in x]
            posts = Post.objects.filter(hashtag__in=list_ht).order_by('-created_at')
            result = database.convert_post(posts)
            return JsonResponse(result, safe=False)
        else:
            return redirect('home:login')


class SetPost(View):
    def post(self, request):
        if request.user.is_authenticated:
            content = request.POST.get('content')
            hashtag = request.POST.get('hashtag').upper().replace(" ", "")
            feeling = request.POST.get('feeling')
            tag_friends = request.POST.get('tag_friends')
            public = request.POST.get('public')
            photo = ''
            try:
                photo = request.FILES['photo']
            except:
                pass
            new_post = Post()
            new_post.content = content
            new_post.photo = photo
            new_post.hashtag = hashtag
            new_post.feeling = feeling
            new_post.tag_friends = tag_friends
            new_post.public = public
            new_post.user = request.user
            new_post.save()
            return redirect('post:ShowPost', new_post.post)


class EditPost(View):
    def get(self, request, post_id):
        if request.user.is_authenticated:
            return render(request, 'post/edit_post.html', {'post_id': post_id, 'page': 'Bài viết với ID là'})
        else:
            return redirect('home:home')

    def post(self, request, post_id):
        if request.user.is_authenticated:
            get_post = Post.objects.get(post=post_id)
            if request.method == 'POST':
                try:
                    photo = request.FILES['photo']
                    get_post.photo = photo
                except:
                    pass
                get_post.content = request.POST.get('content')
                get_post.hashtag = request.POST.get('hashtag').upper()
                get_post.feeling = request.POST.get('feeling')
                get_post.public = request.POST.get('public')
                get_post.save()
            return redirect('post:ShowPost', post_id)
        else:
            return redirect('home:home')


class DeletePost(View):
    def post(self, request):
        if request.user.is_authenticated:
            data = json.loads(request.body.decode('utf-8'))
            get_post = Post.objects.get(post=data['post_id'])
            if get_post.user_id == request.user.id:
                get_post.delete()
            return HttpResponse('Xóa Thành công')

        else:
            return HttpResponse('Tài khoản chưa đăng nhập')


class ApiHashtag(View):
    def get(self, request, hashtag):
        if request.user.is_authenticated:
            return render(request, 'home/home.html', {'hashtag_post': hashtag, 'page': 'Bài viết với Hashtag'})
        else:
            return redirect('home:home')

    def post(self, request, hashtag):
        if request.user.is_authenticated:
            posts = Post.objects.filter(hashtag=hashtag.upper()).order_by('-created_at')
            database = Database()
            result = database.convert_post(posts)
            return JsonResponse(result, safe=False)
        else:
            return redirect('home:login')


class ApiTopHashtag(View):
    def post(self, request):
        if request.user.is_authenticated:
            x = list(Post.objects.all().values('hashtag').annotate(soluot=Count('hashtag')).order_by('-soluot'))
            return JsonResponse({'result': x[0:10]})
        else:
            return redirect('home:login')


class Comment_post(View):
    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        try:
            if data['content_input']:
                new_cm = Comment()
                new_cm.content = data['content_input']
                new_cm.user_id = request.user.id
                new_cm.post_id = data['post_id']
                new_cm.save()
                return HttpResponse('bình luận thành công, hãy tiếp tục tương tác nhé')
        except:
            pass
        z = Comment.objects.filter(post=data['post_id']).order_by('-created_at')
        comments = []
        for i in z:
            d = model_to_dict(i.user)
            del d['password'], d['cover_image'], d['avatar'], d['email'], d['date_joined']
            out = {**model_to_dict(i), **d, "created_at": i.created_at.strftime("%H:%M:%S ngày %m/%d/%Y")}
            comments.append(out)
        return JsonResponse(comments, safe=False)


class Delete_comment(View):
    def post(self, request):
        if request.user.is_authenticated:
            data = json.loads(request.body.decode('utf-8'))
            get_comment = Comment.objects.get(comment=data['comment_id'])
            if get_comment.user == request.user:
                get_comment.delete()
                return HttpResponse('Bạn vừa xóa thành công bình luận của mình')
            return HttpResponse('Bạn không thể xóa bình luận của người khác')
        else:
            return HttpResponse('Phiên đăng nhập  này đã hết hạn. vui lòng đăng nhập lại')
