"""
models : 데이터 정의. 테이블을 만드는 부분
"""

from django.db import models

# Create your models here.


class Addresses(models.Model):
    name = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=13)
    address = models.TextField()
    created = models.DateTimeField(auto_now_add=True) # 객체를 생성하는 시간을 자동으로 넣어준다

    class Meta:
        ordering = ['created']

