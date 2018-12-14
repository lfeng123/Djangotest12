from rest_framework.generics import CreateAPIView, GenericAPIView
from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.mixins import CreateModelMixin

from mmmeiduo.apps.users.models import User
from mmmeiduo.apps.users.serializers import CreateSerializers


class UserNameCountView(APIView):
    def get(self, request, username):
        # 查询用户数量
        count = User.objects.filter(username=username).count()

        return Response({
            'count': count,

        })


class MobileCountView(APIView):
    def get(self, request, mobile):
        # 查询用户数量
        count = User.objects.filter(mobile=mobile).count()

        return Response({

            'count': count,
        })


class UserView(CreateAPIView):


    serializer_class = CreateSerializers
    queryset = User.objects.all()
