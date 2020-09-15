"""
serializers : 모델로 만든 데이터를 json 형태로 간단하게 바꿔주는 역할
"""

from rest_framework import serializers
from .models import Addresses


# 객체 데이터를 넣으면 사용하고자 하는 모델의 필드만 json 으로 바꿔서 출력해준다
class AddressesSerializer(serializers.ModelSerializer):
    class Meta:  # 사용할 모델, 사용할 필드 적는다
        model = Addresses
        fields = ['name', 'phone_number', 'address']