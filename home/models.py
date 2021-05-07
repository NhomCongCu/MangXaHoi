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

    # Lấy toàn bộ bài đăng của tài khoản đang theo dõi
    def get_post_index(self):
        sql = "SELECT * FROM post_post a JOIN user_myuser b ON a.user_id =  b.id WHERE (a.user_id IN(SELECT followres_id FROM user_follower WHERE main_user_id = " + self.userid + ") OR a.user_id = " + self.userid + ")  AND a.public != 'Chỉ Mình Tôi' ORDER BY a.created_at DESC"
        return Post.objects.raw(sql)

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
        # sql = "SELECT * FROM user_myuser a WHERE a.username ='" + str(username) + "'"
        username = MyUser.objects.filter(username=username)
        a = []
        for i in username:
            d = model_to_dict(i)
            print("===============================")
            print("===============================")
            print(type(d["avatar"]))

            print("===============================")
            print("===============================")
            # d["category"] = model_to_dict(i.category)
            # d["spending"] = model_to_dict(i.spending)
            # d["wallet"] = model_to_dict(i.wallet)
            a.append(d)
        # get_profile = MyUser.objects.raw(sql)
        profile = []
        for i in username:
            thisdict = {}
            thisdict["username"] = i.username
            thisdict["user_id"] = i.id
            thisdict["email"] = i.email
            thisdict["avatar"] = str(i.avatar)
            thisdict["cover_image"] = str(i.cover_image)
            thisdict["first_name"] = i.first_name
            thisdict["last_name"] = i.last_name
            thisdict["full_name"] = i.first_name + " " + i.last_name
            thisdict["birthday"] = i.birthday
            thisdict["gender"] = i.gender
            thisdict["address"] = i.address
            thisdict["intro"] = i.intro
            thisdict["date_joined"] = i.date_joined.strftime("%H:%M:%S ngày %m/%d/%Y")
            thisdict["is_superuser"] = i.is_superuser
            profile.append(thisdict)
            print(a)
            print(profile)
        return profile

    # Lấy ra tất cả bài viết của username nhập vào
    def get_profile_posts(self, username, session_user):
        if username != session_user:
            sql = "SELECT * FROM post_post a JOIN user_myuser b ON a.user_id =  b.id WHERE b.username ='" + str(
                username) + "'  AND a.public != 'Chỉ Mình Tôi' ORDER BY created_at DESC"
        else:
            sql = "SELECT * FROM post_post a JOIN user_myuser b ON a.user_id =  b.id WHERE b.username ='" + str(
                username) + "' ORDER BY created_at DESC"
        get_profile_posts = Post.objects.raw(sql)
        profile_posts = []
        for i in get_profile_posts:
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
            profile_posts.append(thisdict)
        return profile_posts

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
        sql = "SELECT * FROM user_myuser a JOIN (SELECT * FROM user_follower WHERE main_user_id = " + str(
            user_id) + ") b ON a.id = b.followres_id WHERE  a.id !='" + str(user_id) + "'"
        get_watching = MyUser.objects.raw(sql)
        profile_watching = []
        for i in get_watching:
            thisdict = {}
            thisdict["avatar"] = str(i.avatar)
            thisdict["username"] = i.username
            thisdict["full_name"] = i.first_name + " " + i.last_name
            thisdict["id"] = i.id
            profile_watching.append(thisdict)
        return profile_watching

    # lấy ra các tài khoản đang theo dõi username (được theo dõi)
    def get_followed(self, username):
        user_id = self.username_convert_id(username)
        sql = "SELECT * FROM user_myuser a JOIN (SELECT * FROM user_follower WHERE followres_id ='" + str(
            user_id) + "') b ON a.id = b.main_user_id WHERE  a.id !='" + str(user_id) + "'"
        get_followed = MyUser.objects.raw(sql)
        profile_followed = []
        for i in get_followed:
            thisdict = {}
            thisdict["avatar"] = str(i.avatar)
            thisdict["username"] = i.username
            thisdict["full_name"] = i.first_name + " " + i.last_name
            thisdict["id"] = i.id
            profile_followed.append(thisdict)
        return profile_followed

    # Lấy tất cả người dùng mà tài khoản đăng nhập chưa theo dõi
    def get_all_user(self):
        sql = "SELECT * FROM user_myuser WHERE id !=" + self.userid + " AND id NOT IN (SELECT followres_id FROM user_follower c WHERE c.main_user_id = " + self.userid + " ) Order by date_joined DESC"
        get_all_user = MyUser.objects.raw(sql)
        all_user = []
        for i in get_all_user:
            thisdict = {}
            thisdict["id"] = i.id
            thisdict["username"] = i.username
            thisdict["avatar"] = str(i.avatar)
            thisdict["full_name"] = i.first_name + " " + i.last_name
            all_user.append(thisdict)
        return all_user

    # kiểm tra xem đã theo dõi chưa

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
