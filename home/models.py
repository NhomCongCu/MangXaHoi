import os
import random

from django.db.models import Count
from django.forms import model_to_dict

from post.models import Post, Comment
from user.models import MyUser, Conversation, Message, Follower


class ShiliEmail:
    def form_mail(self, url, content, email, type='welcome'):
        module_dir = os.path.dirname(__file__)
        if type == 'welcome':
            file_path = os.path.join(module_dir, 'stactic/mail/welcome.html')
        else:
            file_path = os.path.join(module_dir, 'stactic/mail/pass.html')

        with open(file_path, "r", encoding='utf-8') as f:
            data = f.read()
        data = data.replace('@@@content@@@', content)
        data = data.replace('@@@link@@@', url)
        data = data.replace('@@@mail@@@', email)
        return data


class MaHoaOneTimePad:
    def __init__(self):
        self.charset = "v4b7zt9c8fwj5ok0.h6euqai1@lxrgd2yms_pn3".lower()
        # self.charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@_.".lower()

    def ma_hoa(self, plaintext):
        otp = "".join(random.sample(self.charset, len(self.charset)))
        result = ""
        for c in plaintext.lower():
            if c not in otp:
                continue
            else:
                result += otp[self.charset.find(c)]
        return otp, result

    def giai_ma(self, otp, secret):
        result = ""
        for c in secret.lower():
            if c not in otp:
                continue
            else:
                result += self.charset[otp.find(c)]
        return result


class Database:
    def convert_post(self, data):
        out = []
        for i in data:
            d = {**model_to_dict(i), **model_to_dict(i.user)}
            d["photo"] = d["photo"].name
            d["avatar"] = d["avatar"].name
            d["created_at"] = i.created_at.strftime("%H:%M:%S ngày %m/%d/%Y")
            del d['password'], d['cover_image']
            out.append(d)
        return out


    # kiểm tra xem đã có phòng chat chưa
    def check_box_chat(self, user_1, user_2):
        x = Conversation.objects.filter(user_1=user_1, user_2=user_2)
        y = Conversation.objects.filter(user_1=user_2, user_2=user_1)
        if x:
            return model_to_dict(x[0])["c_id"]
        elif y:
            return model_to_dict(y[0])["c_id"]
        else:
            return False


    # trả về toàn bộ thông tin người dùng với username
    def get_profile(self, username):
        username = MyUser.objects.filter(username=username)
        data = []
        for i in username:
            d = model_to_dict(i)
            d["avatar"] = d["avatar"].name
            d["cover_image"] = d["cover_image"].name
            del d['password']
            data.append(d)
        return data

    # Lấy ra tất cả bài viết của username nhập vào
    def get_profile_posts(self, username, session_user):
        if username != session_user:
            x = Post.objects.filter(user__username=username).select_related('user').exclude(
                public='Chỉ Mình Tôi').order_by('-created_at')
        else:
            x = Post.objects.filter(user__username=username).order_by('-created_at')
        data = []
        for i in x:
            d = {**model_to_dict(i), **model_to_dict(i.user)}
            d["photo"] = d["photo"].name
            d["avatar"] = d["avatar"].name
            d["created_at"] = i.created_at.strftime("%H:%M:%S ngày %m/%d/%Y")
            del d['password'], d['cover_image']
            data.append(d)
        return data

    # lấy ra các tài khoản mà username đang theo dõi
    def get_watching(self, username):
        user_id = MyUser.objects.get(username=username).id
        a = Follower.objects.filter(main_user=user_id).values('followres')
        x = [i["followres"] for i in a]
        data = MyUser.objects.filter(id__in=x).values('id', 'username', 'avatar', 'first_name', 'last_name')
        return [i for i in data]

    # lấy ra các tài khoản đang theo dõi username (được theo dõi)
    def get_followed(self, username):
        user_id = MyUser.objects.get(username=username).id
        a = Follower.objects.filter(followres=user_id).values('main_user')
        x = [i["main_user"] for i in a]
        data = MyUser.objects.filter(id__in=x).values('id', 'username', 'avatar', 'first_name', 'last_name')
        return [i for i in data]

