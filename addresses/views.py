"""
views : 특정 기능과 템플릿을 제공하는 웹페이지의 한 종류
"""

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Addresses
from .serializers import AddressesSerializer
from rest_framework.parsers import JSONParser
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import json
from .faq_chatbot import faq_answer


# 주소록 전체를 조회하거나 신규 주소를 생성
@csrf_exempt
def address_list(request):  # request - 호출
    if request.method == 'GET':  # GET : 전체조회
        query_set = Addresses.objects.all()  # 모든 객체를 다 읽어온다
        serializer = AddressesSerializer(query_set, many=True)  # 읽어온 객체를 serializer 에 넣어서 json 형태로 반환
        return JsonResponse(serializer.data, safe=False)  # return은 항상 Response 형태여야 한다.

    elif request.method == 'POST':  # POST : 신규생성
        data = JSONParser().parse(request)  # JSONParser를 통해 request를 읽어옴 → 만들어야하는 객체 데이터가 JSON 형태이기 때문
        serializer = AddressesSerializer(data=data)  # 파싱한 데이터를 serializer에 넣는다
        if serializer.is_valid():  # serializer에서 선언했던 모델, 필드와 비교해서 일치한다
            serializer.save()  # save()를 통해 객체 생성
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)


# 주소록 하나를 조회하거나 수정, 삭제
@csrf_exempt
def address(request, pk):
    obj = Addresses.objects.get(pk=pk)  # 하나의 객체를 선택해서 처리해야하기 때문에 pk(primary key)를 통해 하나를 조회

    if request.method == 'GET':  # GET : 조회
        serializer = AddressesSerializer(obj)  # 읽어온 하나의 객체를 serializer 에 넣어서 json 형태로 반환
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'PUT':  # PUT : 수정
        data = JSONParser().parse(request)   # JSONParser를 통해 request를 읽어옴 → 만들어야하는 객체 데이터가 JSON 형태이기 때문
        serializer = AddressesSerializer(obj, data=data)  # (선택된 객체, 파싱한 데이터)를 serializer에 넣는다 → 신규 생성이 아니라 수정이기 때문에 대상을 넣어야한다.
        if serializer.is_valid():
            serializer.save()  # save()를 통해 객체 생성
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':  # DELETE : 삭제
        obj.delete()  
        return HttpResponse(status=204)


@csrf_exempt
def login(request):

    if request.method == 'POST':
        print("리퀘스트 로그" + str(request.body))
        id = request.POST.get('userid','')
        pw = request.POST.get('userpw', '')
        print("id = " + id + " pw = " + pw)

        result = authenticate(username=id, password=pw)

        if result :
            print("로그인 성공!")
            return HttpResponse(status=200)
        else:
            print("실패")
            return HttpResponse(status=401)

    return render(request, 'addresses/login.html')


@csrf_exempt
def app_login(request):

    if request.method == 'POST':
        print("리퀘스트 로그" + str(request.body))
        id = request.POST.get('userid', '')
        pw = request.POST.get('userpw', '')
        print("id = " + id + " pw = " + pw)

        result = authenticate(username=id, password=pw)

        if result:
            print("로그인 성공!")
            return JsonResponse({'code': '0000', 'msg': '로그인성공입니다.'}, status=200)
        else:
            print("실패")
            return JsonResponse({'code': '1001', 'msg': '로그인실패입니다.'}, status=200)


# 챗봇
@csrf_exempt
def chat_service(request):
    if request.method == 'POST':
        input1 = request.POST['input1']
        response = faq_answer(input1)
        output = dict()
        output['response'] = response
        return HttpResponse(json.dumps(output), status=200)
    else:
        return render(request, 'addresses/chat_test.html')