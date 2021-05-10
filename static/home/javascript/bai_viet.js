axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN"

let home = new Vue({
    el: '#home',
    delimiters: ['[[', ']]'],
    data() {
        return {
            domain: window.location.origin,
            page: $("#data").attr("page"),
            user_id: $("#data").attr("user_id"),
            email: $("#data").attr("email"),
            username: $("#username").attr("username"),

            hashtag_post: $("#data_post").attr("hashtag_post"),
            get_profile: {},
            api_get_all_user: {},
            api_top_hashtag: {},
            api_your_friend: {},
            api_post: {},
            search: null,
            thongBao: [],
            themes: 'thongtin',
            show_bar: false,
            edit: {
                first_name: '',
                first_name1: '',
                last_name: '',
                intro: '',
                email: '',
                address: '',
                gender: '',
                birthday: '',
            },
            edit_av_bg: {
                avatar: '',
                cover_image: '',
                results: '',
            },
            chat_content: {},
            run_Interval_chat: null,
            run_Interval_cmt: false,
            chat: {
                input: null,
                input1: null,
                boxchat: {},
                chat_content: {},
                boxchat_on: false,
            },
            comment: [],
            comment_data: [],


        }
    },
    created: function () {
        this.get_api_top_hashtag();
        this.get_api_your_friend();

        switch (this.page) {
            case 'profile':
                this.get_profile_func()
                break;
            case 'all_user':
                this.api_get_all_user_func();
                break;
        }
    },
    watch: {
        thongBao: function () {
            setTimeout(() => this.thongBao.shift(), 5000);
        }
    },

    methods: {
        get_profile_func: function () {
            axios({
                method: 'post',
                url: '/profile/api/getprofile/',
                data: {
                    username: this.username
                },
            }).then(response => {
                this.get_profile = response.data;
                this.api_post = this.get_profile.profile_posts;
            })
        },


        get_api_top_hashtag: function () {
            axios({
                method: 'post',
                url: '/post/api/top_hashtag/',
            }).then(response => {
                this.api_top_hashtag = response.data;
            });
        },
        get_api_your_friend: function () {
            axios({
                method: 'post',
                url: '/profile/api/your_friend/',
            }).then(response => {
                this.api_your_friend = response.data;
            });
        },


        api_get_all_user_func: function () {
            axios({
                method: 'post',
                url: '/profile/alluser/',
            }).then(response => {
                this.api_get_all_user = response.data;
            })
        },

        scrollToTop() {
            window.scrollTo(0, 0);
        },





        forgotPass_func: function (email) {
            if (email === this.email) {
                axios({
                    method: 'post',
                    url: '/sendpass/',
                    data: {
                        email: email,
                    },
                }).then(response => {
                    this.thongBao.push(response.data)
                    this.get_profile_func();
                })
            } else {
                this.thongBao.push('Bạn không phải chủ tài khoản này')
            }
        },
        check_friend: function (user_id) {
            for (let a of this.api_your_friend.result) {
                if (a.id === user_id) {
                    return true;
                }
            }
            return false;
        },
        add_follow: function (friends_id) {
            axios({
                method: 'post',
                url: "/profile/add_follow/",
                data: {
                    id: friends_id,
                },
            }).then(response => {
                if (this.username) {
                    this.get_profile_func();
                }
                this.api_get_all_user_func()
                this.get_api_your_friend();
                this.thongBao.push(response.data)
            })
        },
        comment_func: function (post_id, i) {
            if (home.comment[i]) {
                axios({
                    method: 'post',
                    url: '/post/comments/',
                    data: {
                        content_input: home.comment[i],
                        post_id: post_id,
                    },
                }).then(response => {
                    home.comment[i] = null;
                    if (this.comment_data[i] === false) {
                        this.comment_show_func(post_id, i);
                    } else {
                        this.get_cmt(post_id, i);
                    }
                    this.thongBao.push(response.data)
                })
            }
        },
        get_cmt: function (post_id, i) {
            axios({
                method: 'post',
                url: '/post/comments/',
                data: {
                    post_id: `${post_id}`,
                },
            }).then(response => {
                home.comment_data[i] = response.data;
            })
        },
        comment_show_func: function (post_id, i) {
            x = this.comment_data[i]
            if (x != false) {
                clearInterval(this.run_Interval_cmt)
                this.get_cmt(post_id, i)
                this.run_Interval_cmt = setInterval(function () {
                    home.get_cmt(post_id, i)
                }, 1000);
            } else {
                this.comment_data[i] = false;
                clearInterval(this.run_Interval_cmt)
            }
        },
        comment_delete_func: function (post_id, comment_id, i) {
            axios({
                method: 'post',
                url: '/post/delete_comment/',
                data: {
                    post_id: post_id,
                    comment_id: comment_id,
                },
            }).then(response => {
                this.get_cmt(post_id, i);
                this.thongBao.push(response.data)
            })

        },
        get_mess_content: function (user_2_id) {
            axios({
                method: 'post',
                url: "/chat/",
                data: {
                    user_2_id: user_2_id,
                },
            }).then(response => {
                home.chat_content = response.data['mess_content'];
                home.chat.boxchat = response.data['result'];
            })
        },
        show_box_chat: function () {
            home.chat.boxchat_on = false;
            clearInterval(this.run_Interval_chat);


        },
        chat_box_func: function (user_2_id) {
            home.chat.boxchat_on = true;
            home.get_mess_content(user_2_id);
            this.run_Interval_chat = setInterval(function () {
                home.get_mess_content(user_2_id);
            }, 500)
            axios({
                method: 'post',
                url: "/chat/",
                data: {
                    user_2_id: user_2_id,
                },
            }).then(response => {
                home.chat.boxchat = response.data['result'];
                this.scrollBottom();
            })

        },
        send_mess_func: function (user_2_id) {
            axios({
                method: 'post',
                url: "/chat/save_mess/",
                data: {
                    user_2_id: user_2_id,
                    content: this.chat.input,
                },
            }).then(response => {
                home.chat.input = '';
                home.get_mess_content(user_2_id);
                this.scrollBottom();
            })

        },
        delete_mess_func: function (m_id, from_user_id) {
            home.chat.boxchat_on = true;
            axios({
                method: 'post',
                url: "/chat/delete_mess/",
                data: {
                    m_id: m_id,
                    from_user_id: from_user_id,
                },
            }).then(response => {
                this.thongBao.push(response.data)
            })
        },
        scrollBottom: function () {
            let container = home.$el.querySelector("#container");
            container.scrollTop = container.scrollHeight;
        },
        open_link: function (link) {
            window.open(`${link}`, "_self");
        },
    },
})

