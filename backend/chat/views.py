from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken


@api_view (['GET'])
# Create your views here.
def health_check(request):
    return Response({'status': 'ok'})


@api_view (['POST'])
def register(request):
    username=request.data.get('username')
    password=request.data.get('password')

    if not username or not password:
        return Response(
            {"error" : "username and password are required"},
             status =status.HTTP_400_BAD_REQUEST
        )   
    
    if username.objects.filter(username=username).exists():
        return Response(
            {"error": "username already exists"},
            status=status.HTTP_400_BAD_REQUEST
        )
    user = User.objects.create_user(username=username, password=password)

    user=User.objects.create_user(username=username, password=password)
    refresh = RefreshToken.for_user(user)    

    return Response ({
        "message": "user created succesfully",
        "refresh": str(refresh),
        "access": str(refresh.access_token)
    },status = status.HTTP_201_CREATED)

@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    # check if the field are empty
    if not username or not password:
        return Response(
            {"error": "username amd password are reuired"},
            status=status.HTTP_400_BAD_REQUEST
        )
    # find the user
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response (
            {"error ": "invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED

        )
    # check the password
    if not user.check_password(password):
        return Response(
            {"error":"invalid credientials"},
            status = status.HTTP_401_UNAUTHORIZED
        )
    
    refresh = RefreshToken.for_user(user)
    return Response({
        "message": "loggin succesfully",
        "access": str(refresh.access_token),
        "refresh": str(refresh),

    })