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
    def __init__(self, userid):
        self.userid = str(userid)

    # Lấy toàn bộ bài đăng của cacs tài khoản đang theo dõi

    # Lấy ra thông tin 1 bài viết với id cụ thể
    def get_post_id(self, post_id):
        sql = "SELECT * FROM post_post a JOIN user_myuser b ON a.user_id =  b.id WHERE a.post = '" + str(
            post_id) + "'"
        return Post.objects.raw(sql)

    #  Trả về json thông tin bài viết
    def json_post(self, get_post):
        posts = []
        for i in get_post:
            thisdict = {}
            thisdict["post_id"] = i.post
            thisdict["username"] = i.username
            thisdict["full_name"] = i.first_name + " " + i.last_name
            thisdict["feeling"] = i.feeling
            thisdict["created_at"] = i.created_at.strftime("%H:%M:%S ngày %m/%d/%Y")
            thisdict["public"] = i.public
            thisdict["content"] = i.content
            thisdict["hashtag"] = i.hashtag
            thisdict["user_id"] = i.user_id
            thisdict["avatar"] = str(i.avatar)
            thisdict["photo"] = str(i.photo)
            posts.append(thisdict)
        return posts

    # Lấy ra thông tin bài viết nằm trong top x hashtag nổi bật
    def get_post_in_top_x_hashtag(self, limit):
        sql = "SELECT * FROM post_post a JOIN user_myuser b ON a.user_id =  b.id JOIN( SELECT hashtag,count(hashtag) AS SoLuot FROM post_post GROUP BY hashtag  ORDER BY SoLuot DESC LIMIT " + limit + ") c ON a.hashtag =c.hashtag"
        return Post.objects.raw(sql)

    # Lấy id bài viết mới đăng gần nhất của tài khoản đăng nhập
    def get_id_new_post(self):
        sql = 'SELECT post From user_myuser a JOIN post_post b on a.id =  b.user_id ORDER BY created_at DESC LIMIT 1'
        return Post.objects.raw(sql)[0].post

    # Lấy ra thông tin bài viết cho hashtag bất kì
    def get_post_hashtag(self, hashtag):
        sql = "SELECT * FROM post_post a JOIN user_myuser b ON a.user_id =  b.id WHERE a.hashtag = '" + hashtag + "'"
        return Post.objects.raw(sql)

    # trả về tất cả comments của bài viết với post_id
    def get_comment_post_id(self, post_id):
        sql = "SELECT * FROM post_comment a JOIN user_myuser b ON  a.user_id = b.id WHERE a.post_id =" + str(
            post_id)
        comment_post_id = []
        for i in Comment.objects.raw(sql):
            thisdict = {}
            thisdict["content"] = i.content
            thisdict["user_id"] = i.user_id
            thisdict["username"] = i.username
            thisdict["comment_id"] = i.comment
            thisdict["fullname"] = i.first_name + i.last_name
            thisdict["created_at"] = i.created_at.strftime("%H:%M:%S ngày %m/%d/%Y")
            thisdict["post_id"] = i.post_id
            comment_post_id.append(thisdict)
        return comment_post_id

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

    # Chuyển đổi username thành id
    def username_convert_id(self, username):
        user_id_sql = "SELECT id FROM user_myuser WHERE username ='" + str(username) + "'"
        return MyUser.objects.raw(user_id_sql)[0].id

    # Chuyển đổi id thành username
    def id_convert_username(self, id):
        user_id_sql = "SELECT username FROM user_myuser WHERE id =" + str(id)
        return MyUser.objects.raw(user_id_sql)[0].username

    # lấy ra các tài khoản mà username đang theo dõi
    def get_watching(self, username):
        user_id = self.username_convert_id(username)
        a = Follower.objects.filter(main_user=user_id).values('followres')
        x = [i["followres"] for i in a]
        data = MyUser.objects.filter(id__in=x).values('id', 'username', 'avatar', 'first_name', 'last_name')
        return [i for i in data]

    # lấy ra các tài khoản đang theo dõi username (được theo dõi)
    def get_followed(self, username):
        user_id = self.username_convert_id(username)
        a = Follower.objects.filter(followres=user_id).values('main_user')
        x = [i["main_user"] for i in a]
        data = MyUser.objects.filter(id__in=x).values('id', 'username', 'avatar', 'first_name', 'last_name')
        return [i for i in data]

    # Lấy tất cả người dùng mà tài khoản đăng nhập chưa theo dõi
    def get_all_user(self):
        data = Follower.objects.filter(main_user=self.userid).values('followres_id')
        x = [i["followres_id"] for i in data]
        data = MyUser.objects.all().exclude(id__in=[int(self.userid)] + x).values('id', 'username', 'avatar',
                                                                                  'first_name', 'last_name')
        return [i for i in data]

    # kiểm tra xem đã có phòng chat chưa
    def check_box_chat(self, user_1, user_2):
        x = Conversation.objects.filter(user_1=user_1, user_2=user_2)
        y = Conversation.objects.filter(user_1=user_2, user_2=user_1)
        try:
            c_id = model_to_dict(x[0])["c_id"]
        except:
            pass
        try:
            c_id = model_to_dict(y[0])["c_id"]
        except:
            pass
        if x or y:
            return c_id
        else:
            return False

    # lấy nội dung chat của phòng chat
    def get_context_box_chat(self, conversation):
        data = Message.objects.filter(conversation=conversation)
        a = []
        for i in data:
            d = model_to_dict(i)
            d["created_at"] = i.created_at.strftime("%H:%M:%S ngày %m/%d/%Y")
            a.append(d)
        return a
