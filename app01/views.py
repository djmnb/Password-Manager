import datetime
import random
from io import BytesIO

import django.http
from django.core.mail import send_mail
from django.http import HttpRequest, JsonResponse
from django.http import HttpResponse
from django.shortcuts import render, redirect
import django.forms as forms

# Create your views here.
from app01.models import User, Password

# class UserModelForm(forms.ModelForm):
#
#
#     class Meta:
#         model = User
#         fields = ["name","email","password","ip"]
#
#     def __init__(self,*args,**kwargs):
#         super().__init__(*args,**kwargs)
#
#         for name,field in self.fields.items():
#             field.widget.attrs = {"class":"form-control","placeholder": field.label,"name":name}
#
from app01.utils import util
from app01.utils.code import check_code
from 密码管理系统 import settings


# class LoginForm(forms.Form):
#     name = forms.CharField(max_length=20, min_length=5, widget=forms.TextInput(attrs={
#         "class": "form-control",
#         "placeholder": "请输入用户名"
#     }), label="用户名")
#
#     password = forms.CharField(max_length=20, min_length=8, widget=forms.PasswordInput(attrs={
#         "class": "form-control",
#         "placeholder": "请输入密码"
#     }), label="密码")
#
#     img_code = forms.CharField(max_length=10,widget=forms.TextInput(attrs={
#
#     }))

class RegisterForm(forms.Form):
    name = forms.CharField(max_length=20, min_length=5, widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "请输入用户名"
    }), label="用户名")

    password = forms.CharField(max_length=20, min_length=8, widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "请输入密码",
        "type": "password"
    }), label="密码")

    repassword = forms.CharField(max_length=20, min_length=8, widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "请输入确认密码",
        "type": "password"
    }), label="确认密码")

    email = forms.EmailField(max_length=30, widget=forms.EmailInput(attrs={
        "class": "form-control",
        "placeholder": "请输入邮箱"
    }), label="邮箱")

    def clean_name(self):
        name = self.cleaned_data.get("name")
        user = User.objects.filter(name=name).first()
        if user:
            self.add_error("name", "用户名已经存在")
        return name

    def clean(self):
        password = self.cleaned_data.get("password")
        repassword = self.cleaned_data.get("repassword")

        if password != repassword:
            self.add_error("repassword", "两次密码不一致")
        return self.cleaned_data


def login(requset: HttpRequest):
    if requset.method == 'GET':
        return render(requset, "login.html", {"img_error": "", "msg": ""})

    name = requset.POST.get("name")
    password = requset.POST.get("password")
    img_code = requset.POST.get("code")

    if img_code.lower() != requset.session["imgcode"].lower():
        return render(requset, "login.html", {"img_error": "验证码错误", "name": name,"password":password})

    print(name)
    print(password)

    user = User.objects.filter(name=name, password=password).first()

    if user:
        requset.session["userinfo"] = {"id": user.id, "name": user.name}
        user.ip = requset.META.get("REMOTE_ADDR")
        user.login_date = datetime.datetime.now()
        print(user.ip)
        print(user.login_date)
        User.objects.filter(id=user.id).update(ip=user.ip, login_date=datetime.datetime.now())
        return redirect("/index")
    else:
        return render(requset, "login.html", {"msg": "账号或者密码错误", "name": name,"password":password})


def register(requset: HttpRequest):
    if requset.method == 'GET':
        form = RegisterForm()
        return render(requset, "register.html", {"form": form})

    form = RegisterForm(data=requset.POST)
    if form.is_valid():
        print(form.cleaned_data)
        print(requset.POST.get("code"),requset.session.get("registercode"))
        if requset.POST.get("code") != requset.session.get("registercode") :
            return render(requset, "register.html", {"form": form, "code_error": "验证码错误"})
        if not util.timeok(requset.session.get("codetime"),datetime.datetime.now().timestamp(),60):
            return render(requset, "register.html", {"form": form, "code_error": "验证码失效"})


        user = User.objects.create(name=form.cleaned_data.get("name"), password=form.cleaned_data.get("password"),
                                   ip=requset.META.get("REMOTE_ADDR"),
                                   login_date=datetime.datetime.now(), email=form.cleaned_data.get("email")
                                   )
        requset.session["userinfo"] = {"id": user.id, "name": user.name}

        user.ip = requset.META.get("REMOTE_ADDR")
        user.login_date = datetime.datetime.now()
        print(user.ip)
        print(user.login_date)
        User.objects.filter(id=user.id).update(ip=user.ip, login_date=datetime.datetime.now())
        return redirect("/index")

    else:
        return render(requset, "register.html", {"form": form})


def index(requset: HttpRequest):
    if requset.method == "GET":
        data = Password.objects.filter(user_id=requset.session.get("userinfo").get("id"))
        return render(requset, "index.html",{"data":data})
    name = requset.POST.get("name")
    data = Password.objects.filter(name__icontains=name,user_id=requset.session.get("userinfo").get("id"))
    return render(requset, "index.html", {"data": data,"name":name})


def logout(requset: HttpRequest):
    requset.session["userinfo"] = ""
    return redirect("/login/")


def send_email(request: HttpRequest):
    print(request.session.get("registercode"))
    if util.timeok(request.session.get("codetime"),datetime.datetime.now().timestamp(),60):
        return JsonResponse({"status": "0", "error": "上次验证码任然有效,请勿重新申请"})
    way = request.GET.get("way")
    try:
        if way == "changepwd":
            subject = '密码管理系统密码更改验证码'  # 主题
        else:
            subject = '密码管理系统注册验证码'  # 主题

        from_email = settings.EMAIL_FROM  # 发件人，在settings.py中已经配置
        to_email = request.GET.get("email")  # 邮件接收者列表


        user = User.objects.filter(email=to_email).first()

        print(user)
        if user and way != "changepwd":
            return JsonResponse({"status": 0, "error": "此邮箱已经注册"})
        if user is None and way == "changepwd":
            return JsonResponse({"status": 0, "error": "该邮箱还未注册"})
        # 发送的消息
        code = ""
        for i in range(6):
            code += str(random.randint(1, 9))

        print(code)
        print(to_email)

        message = code + ",仅1分钟有效哦"  # 发送普通的消息使用的时候message
        # meg_html = '<a href="http://www.baidu.com">点击跳转</a>'  # 发送的是一个html消息 需要指定
        send_mail(subject, message, from_email, [to_email])
        print("发送成功")
        if way == "changepwd":
            request.session["changepwdcode"] = code
        else:
            request.session["registercode"] = code
        request.session["codetime"] = datetime.datetime.now().timestamp()
        # request.session.set_expiry(60)

        return JsonResponse({"status": 1})
    except Exception as e:
        print(e)
        return JsonResponse({"status": 0, "error": "发送失败"})


def get_img(requset: HttpRequest):
    img, code = check_code()
    requset.session["imgcode"] = code

    stream = BytesIO()
    img.save(stream, 'png')

    return HttpResponse(stream.getvalue())


def forgetpwd(requset: HttpRequest):
    if requset.method == "GET":
        return render(requset,"forgetpwd.html")
    email = requset.POST.get("email")
    code = requset.POST.get("code")

    if code == requset.session.get("changepwdcode") and util.timeok(requset.session.get("codetime"),datetime.datetime.now().timestamp(),60):

        user = User.objects.filter(email=email).first()

        if user:
            requset.session["userinfo"] = {"id": user.id, "name": user.name}
            user.ip = requset.META.get("REMOTE_ADDR")
            user.login_date = datetime.datetime.now()
            print(user.ip)
            print(user.login_date)
            User.objects.filter(id=user.id).update(ip=user.ip, login_date=datetime.datetime.now())
            return redirect("/index")
        else:
            return HttpResponse("非法请求")
    return render(requset,"forgetpwd.html",{"codeerror":"验证码错误","email":email})


def edit(requset: HttpRequest, id: int):

    if requset.method == "GET":
        data = Password.objects.filter(id=id).first()
        return render(requset, "editandadd.html", {"data":data,"msg":"修改"})
    name = requset.POST.get("name")
    password = requset.POST.get("password")
    if not name:
        name = ""
    if not password:
        password = ""
    Password.objects.filter(id=id).update(name=name,password=password)
    return redirect("/index")


def add(requset: HttpRequest):

    if requset.method == "GET":
        data = Password()
        return render(requset, "editandadd.html", {"data":data,"msg":"添加"})
    name = requset.POST.get("name")
    password = requset.POST.get("password")
    if not name:
        name = ""
    if not password:
        password = ""
    data = Password.objects.create(name=name,password=password,user_id=requset.session.get("userinfo")["id"])
    data.save()
    return redirect("/index")


def delete(requset: HttpRequest, id: int):
    Password.objects.filter(id=id).delete()
    return redirect("/index")


def test(requset: HttpRequest):
    if requset.method == "GET":
        return render(requset,"test.html",{"data":requset.session})

def changepwd(requset:HttpRequest):

    pwd = ""
    repwd = ""
    error = ""
    success = ""
    if requset.method == "GET":
        return render(requset,"changepwd.html")

    pwd = requset.POST.get("pwd")
    repwd = requset.POST.get("repwd")
    if pwd != repwd:
        error = "两次密码不一致"
        return render(requset,"changepwd.html",locals())
    else:
        success = "更改成功"
        User.objects.filter(id=requset.session.get("userinfo").get("id")).update(password=pwd)
        return render(requset, "changepwd.html", locals())