"""
urls : 각각의 서비스를 연결
"""

from django.conf.urls import url, include
from addresses import views
from django.urls import path
from django.contrib import admin


urlpatterns = [
    path('addresses/', views.address_list),
    path('addresses/<int:pk>/', views.address),
    path('login/', views.login),
    path('app_login/', views.app_login),
    path('admin/', admin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('chat_service/', views.chat_service)
]
