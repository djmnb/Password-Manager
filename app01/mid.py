from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpRequest

class M(MiddlewareMixin):

    def process_request(self, request:HttpRequest):

        admiturl = (
            "/register",
            "/login",
            "/logout",
            "/code",
            "/img/code",
            "/forget",
            "/test",
            "/admin"
        )
        userinfo = request.session.get("userinfo")
        print(userinfo)

        if request.path.startswith("/login") and userinfo:
            return redirect("/index")
        for url in admiturl:
            if request.path.startswith(url):
                return

        # if request.path.startswith("/register") or \
        #     request.path.startswith("/login") or request.path.startswith("/logout") or \
        #     request.path.startswith("/code") or request.path.startswith("/img/code"):
        #
        #     return

        if userinfo:
            return

        return redirect("/login/")


    def process_response(self, request, response):

        return response