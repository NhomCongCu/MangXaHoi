import json

from django.forms import model_to_dict
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.views import View

from home.models import Database
from user.models import Conversation, MyUser, Message


class BoxChat(View):
    def post(self, request):
        if request.user.is_authenticated:
            data = json.loads(request.body.decode('utf-8'))
            user_2_id = str(data['user_2_id'])
            database = Database()
            username = MyUser.objects.get(id=user_2_id)
            get_profile = database.get_profile(username)
            id_room = database.check_box_chat(request.user.id, user_2_id)
            data = Message.objects.filter(conversation=id_room)
            mess_content = []
            for i in data:
                d = model_to_dict(i)
                d["created_at"] = i.created_at.strftime("%H:%M:%S ngày %m/%d/%Y")
                mess_content.append(d)
            if not id_room:
                try:
                    Conv = Conversation()
                    Conv.user_1 = request.user
                    Conv.user_2 = MyUser.objects.get(id=user_2_id)
                    Conv.save()
                except:
                    pass
            get_profile[0]['count_mess'] = len(list(Message.objects.filter(conversation=id_room)))
            return JsonResponse({'result': get_profile, 'mess_content': mess_content}, safe=False)


class SaveMess(View):
    def post(self, request):
        if request.user.is_authenticated:
            data = json.loads(request.body.decode('utf-8'))
            user_2_id = str(data['user_2_id'])
            database = Database()
            id_room = database.check_box_chat(request.user.id, user_2_id)
            # lưu tin nhắn
            if data['content'] != '':
                Mess = Message()
                Mess.from_user = MyUser.objects.get(id=request.user.id)
                Mess.conversation = Conversation.objects.get(c_id=id_room)
                Mess.content = data['content']
                Mess.save()
            return HttpResponse('Gửi thành công rồi nhé Lalal')
        else:
            return redirect('home:home')


class DeleteMess(View):
    def post(self, request):
        if request.user.is_authenticated:
            data = json.loads(request.body.decode('utf-8'))
            m_id = str(data['m_id'])
            get_message = Message.objects.get(m_id=m_id)
            if str(data['from_user_id']) == str(request.user.id) and get_message:
                get_message.delete()
                return HttpResponse('Xóa tin nhắn thành công')
            return HttpResponse('Xóa tin nhắn thất bại')
        else:
            return HttpResponse('Chưa Đăng Nhập')
