axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN"
let index_login = new Vue({
    el: '#index_login',
    delimiters: ['[[', ']]'],
    data: {
        regEX: /^[a-z0-9_-]{3,16}$/,
        login_bg: false,
        themes: '',
        domain: window.location.origin,
        login: {
            username: null,
            password: null,
            result: null,
        },
        password: {
            email: null,
            result: null,
            password1: null,
            password2: null,
            check: false
        },

        sign_up: {
            firstname: null,
            lastname: null,
            username: null,
            email: null,
            password1: null,
            password2: null,
            birthday: null,
            gender: 'Nam',
            checkUserName: null,
            checkEmail: null,
            checkPassword: null,
            result: null,
        },
        intro: null,
        thong_bao: null,

    },
    created: function () {
        try {
            this.themes = document.getElementById("themes").innerHTML;
            if (this.themes) {
                this.login_bg = true;
            }
        } catch (err) {
        }

        axios({
            url: this.domain + '/static/home/Json/login_page.json',
        }).then(response => {
            this.intro = response.data.intro
            this.thong_bao = response.data.thong_bao


        })
    },
    methods: {
        login_func: function () {
            if (!this.login.username) {
                return this.login.result = this.thong_bao.full;
            }
            if (this.regEX.test(this.login.username) || /\S+@\S+\.\S+/.test(this.login.username)) {
                axios({
                    method: 'post',
                    url: '/login/',
                    data: {
                        username: this.login.username.toLowerCase(),
                        password: this.login.password,
                    },
                }).then(response => {
                    this.login.result = response.data;
                    if (this.login.result === 'success') {
                        window.location.href = this.domain;
                    }

                })
            } else {
                return this.login.result = this.thong_bao.sai_format;
            }


        },

        check__: function () {
            axios({
                method: 'post',
                url: '/check/',
                data: {
                    username: this.sign_up.username,
                    email: this.sign_up.email,
                },
            }).then(response => {
                this.sign_up.result = response.data;
            })
        },

        chuyen: function (x) {
            this.themes = 1;
          setTimeout(() => {  this.themes = x }, 500);

        },

        checkUserName_func: function () {
            if (this.sign_up.username) {
                this.sign_up.username = this.sign_up.username.toLowerCase()
                this.check__();
                return this.sign_up.checkUserName = this.regEX.test(this.sign_up.username);
            }
        },
        checkEmail_func: function () {
            this.check__();
            return this.sign_up.checkEmail = /\S+@\S+\.\S+/.test(this.sign_up.email);
        },
        checkPassword_func: function () {
            return this.sign_up.checkPassword = this.sign_up.password1 === this.sign_up.password2 && this.sign_up.password1 !== '' && /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[a-zA-Z]).{8,}$/.test(this.sign_up.password1);
        },
        checkResetPassword: function () {

            return this.password.check = this.password.password1 === this.password.password2 && this.password.password1 !== '' && /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[a-zA-Z]).{8,}$/.test(this.password.password1);
        },
        register_func: function () {
            if (this.checkUserName_func() && this.checkEmail_func() && this.checkPassword_func() && this.sign_up.birthday && this.sign_up.gender && this.sign_up.firstname && this.sign_up.lastname) {
                axios({
                    method: 'post',
                    url: this.domain + '/register/',
                    data: {
                        firstname: this.sign_up.firstname,
                        lastname: this.sign_up.lastname,
                        username: this.sign_up.username.toLowerCase(),
                        email: this.sign_up.email,
                        password1: this.sign_up.password1,
                        birthday: this.sign_up.birthday,
                        gender: this.sign_up.gender,
                    },
                }).then(response => {
                    this.sign_up.result = response.data;
                })
            } else {
                return this.sign_up.result = this.thong_bao.full;
            }

        }
    }
});