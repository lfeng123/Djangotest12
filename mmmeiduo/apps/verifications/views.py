from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView
from random import randint  # 随机生成验证码
from django_redis import get_redis_connection  # 连接缓存数据库redis
from mmmeiduo.libs.yuntongxun.sms import CCP  # 云通讯
from celery_tasks.sms.tasks import send_sms_code # 发送短信的异步任务


class SMSCodeView(APIView):
    def get(self, request, mobile):
        # request.query_pramas # 获取查询字符串
        # request.data # 获取请求体数据

        # 生成短信验证码 random.randint
        # 保存短信验证码 存在redis ,缓存配置
        # 发送短信 云通讯
        # 返回结果

        # 判断60s
        conn = get_redis_connection('verify')
        flag = conn.get('sms_flag_%s' % mobile)
        if flag:
            return Response({'message': '请求过去频繁'})

        # 生成短信验证码
        sms_code = '%06d' % randint(0, 999999)
        print(sms_code)

        # 保存短信验证码
        pl = conn.pipeline()
        pl.setex('sms_%s' % mobile, 300, sms_code)
        pl.setex('sms_flag_%s' % mobile, 60, 2)
        pl.execute() # 发送redis执行命令

        # 发送短信
        ccp = CCP()
        ccp.send_template_sms(mobile, [sms_code, 5], 1)  # 模版文字用1号
        send_sms_code.delay(mobile,sms_code) # 调用异步任务


# celery -A celery_tasks.main worker -l info 开启异步任务
        # 返回结果
        return Response({'message': 'OK'})
