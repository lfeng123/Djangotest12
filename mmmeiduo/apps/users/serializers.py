import re

from django.contrib.auth.models import User
from django_redis import get_redis_connection  # 存储验证码的redis库
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.settings import api_settings  # jwt


class CreateSerializers(ModelSerializer):
    # 显示指明字段
    sms_code = serializers.CharField(max_length=6, write_only=True)
    password2 = serializers.CharField(max_length=20, min_length=8, write_only=True)
    allow = serializers.CharField(write_only=True)
    token = serializers.CharField(read_only=True) # 只进行序列化返回

    class Meta:
        model = User
        fields = ('id', 'name', 'mobile', 'email', 'sms_code', 'password2', 'allow', 'password','token')

        extra_kwargs = {
            'password': {
                'max_length': 20,
                'min_length': 8,
                'write_only': True,
                'error_messages': {
                    'max_length': '密码过长'
                }

            },

            'username': {
                'max_length': 20,
                'min_length': 5,
                'write_only': True,
                'error_messages': {
                    'max_length': '密码过长'
                }

            },

        }

    # 手机号验证
    def validate_mobile(self, value):

        # 匹配手机号格式，用正则
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机格式不正确')

        return value

    # 验证同意协议
    def validate_allow(self, value):
        if value != 'true':
            raise serializers.ValidationError('协议未同意')

        return value

    # 密码验证
    def validate(self, attrs):

        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('两次密码不一致')

        # 短信验证
        # 从redis中获取真实短息
        # 建立连接
        conn = get_redis_connection('verify')

        # 获取数据 （从redis中获取的数据是bytes类型）
        real_sms_code = conn.get('sms_%s' % attrs['mobile'])

        # 判断是否超过有效期
        if not real_sms_code:
            raise serializers.ValidationError('短息失效')

        # 转换数据
        real_sms_code = real_sms_code.decode()

        # 比对验证码
        if attrs['sms_code'] != real_sms_code:
            raise serializers.ValidationError('短息验证码不一致')

        return attrs

    # 保存操作（调用父类）
    def create(self, validated_data):
        del validated_data['sms_code']
        del validated_data['password2']
        del validated_data['allow']

        # user = super().create(validated_data)

        # # 对保存的密码进行加码(set_password进行加码)
        # user.set_password(validated_data['password'])
        # user.save()

        # 管理器方法保存用户
        user = User.objects.create_user(
            username=validated_data.get('username'),
            mobile=validated_data.get('mobile'),
            password=validated_data.get('password'),
        )

        # jwt 结果返回之前，生成token数据
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        user.token = token # 对user对象额外添加token属性


        return user
