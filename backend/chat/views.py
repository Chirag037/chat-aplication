from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Message
from .serializers import RegisterSerializer, LoginSerializer

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({'status': 'ok'})

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "user created successfully",
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }, status=status.HTTP_201_CREATED)
    
    error_msg = next(iter(serializer.errors.values()))[0]
    return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        user = authenticate(username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "login successful",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            })
        else:
            return Response(
                {"error": "invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )
    
    error_msg = next(iter(serializer.errors.values()))[0]
    return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def messages(request):
    if request.method == 'GET':
        room_id = request.query_params.get('room_id', '1')
        msgs = Message.objects.filter(room=room_id).select_related('user')
        data = [{
            "id": m.id,
            "username": m.user.username,
            "content": m.content,
            "room": m.room,
            "created_at": m.created_at
        } for m in msgs]
        return Response(data)

    elif request.method == 'POST':
        content = request.data.get('content')
        room = request.data.get('room', '1')
        if not content:
            return Response({"error": "content is required"}, status=status.HTTP_400_BAD_REQUEST)

        msg = Message.objects.create(user=request.user, content=content, room=room)
        return Response({
            "id": msg.id,
            "username": msg.user.username,
            "content": msg.content,
            "room": msg.room,
            "created_at": msg.created_at
        }, status=status.HTTP_201_CREATED)