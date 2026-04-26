from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db.models import Count, Prefetch
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Message, Room, MessageRead
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, RoomSerializer, MessageSerializer
import requests
import os
import random

Jokes = [
    "Why don't programmers like nature? It has too many bugs.",
    "Why was the computer cold? It left the window open.",
    "Why do Java developers go broke? Because they used up all their cache.",
    "Why did the developer quit his job? Because he didn't get arrays.",
    "Why do programmers prefer dark mode? Because light attracts bugs."
]

@api_view(['GET'])
@permission_classes([AllowAny])
def random_joke(request):
    return Response({
        "joke": random.choice(Jokes)
    })

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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_users(request):
    users = User.objects.exclude(id=request.user.id)
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def room_list(request):
    # Returns only direct message rooms for the current user that have both participants
    rooms = Room.objects.filter(participants=request.user, type='direct') \
        .annotate(p_count=Count('participants')) \
        .filter(p_count=2)
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_group_rooms(request):
    """List all group rooms (public). Auto-create the General room if missing."""
    # Ensure the General room always exists
    Room.objects.get_or_create(name='General', type='group')
    rooms = Room.objects.filter(type='group')
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_group_room(request):
    """Join a group room by id. Creates it if it doesn't exist (for General room seed)."""
    room_id = request.data.get('room_id')
    if not room_id:
        return Response({'error': 'room_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        room = Room.objects.get(id=room_id, type='group')
    except Room.DoesNotExist:
        return Response({'error': 'Group room not found'}, status=status.HTTP_404_NOT_FOUND)
    room.participants.add(request.user)
    serializer = RoomSerializer(room)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_direct_room(request):
    other_user_id = request.data.get('user_id')
    if not other_user_id:
        return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        other_user = User.objects.get(id=other_user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    # Check if direct room already exists
    room = Room.objects.filter(type='direct', participants=request.user).filter(participants=other_user).first()
    
    if not room:
        room = Room.objects.create(type='direct')
        room.participants.add(request.user, other_user)
    
    serializer = RoomSerializer(room)
    return Response(serializer.data)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def messages(request):
    if request.method == 'GET':
        room_id = request.query_params.get('room_id')
        if not room_id or room_id == 'null':
            return Response({"error": "room_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            room = Room.objects.get(id=room_id, participants=request.user)
        except Room.DoesNotExist:
            return Response({"error": "Room not found or access denied"}, status=status.HTTP_403_FORBIDDEN)

        reads_qs = MessageRead.objects.select_related('user').order_by('read_at')
        msgs = Message.objects.filter(room=room).select_related('user', 'room').prefetch_related(
            Prefetch('reads', queryset=reads_qs)
        )
        serializer = MessageSerializer(msgs, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        content = request.data.get('content')
        room_id = request.data.get('room')
        message_type = request.data.get('message_type', 'text')
        attachment = request.FILES.get('attachment')
        
        if not room_id or room_id == 'null':
            return Response({"error": "room is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not content and not attachment:
            return Response({"error": "content or attachment is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            room = Room.objects.get(id=room_id, participants=request.user)
        except Room.DoesNotExist:
            return Response({"error": "Room not found or access denied"}, status=status.HTTP_403_FORBIDDEN)

        msg = Message.objects.create(
            user=request.user, 
            content=content, 
            room=room, 
            message_type=message_type, 
            attachment=attachment
        )
        serializer = MessageSerializer(msg)
        
        # Broadcast message via WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chat_{room_id}',
            {
                'type': 'chat_message',
                'message': msg.content,
                'username': request.user.username,
                'created_at': msg.created_at.isoformat(),
                'id': msg.id,
                'room_type': room.type,
                'message_type': msg.message_type,
                'attachment': serializer.data['attachment'],
            }
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def ai_proxy(request):
    """Generic proxy for AssemblyAI requests to solve CORS and security issues."""
    path = request.query_params.get('path', 'v2/llm/completions')
    url = f'https://api.assemblyai.com/{path}'
    
    api_key = "5734a76428f8474ab5ac0b7bc8dac395"
    
    headers = {
        'authorization': api_key,
    }
    
    try:
        if request.method == 'GET':
            response = requests.get(url, headers=headers, timeout=60)
        else:
            # For POST requests
            content_type = request.content_type
            if content_type == 'application/octet-stream' or 'audio' in content_type:
                # Handle binary file uploads
                response = requests.post(url, data=request.body, headers=headers, timeout=120)
            else:
                # Handle JSON data
                response = requests.post(url, json=request.data, headers=headers, timeout=60)
        
        # Return JSON if possible, else raw text
        try:
            return Response(response.json(), status=response.status_code)
        except:
            return Response({'content': response.text, 'status': response.status_code}, status=response.status_code)
            
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ollama_proxy(request):
    """Proxy for local Ollama requests."""
    prompt = request.data.get('prompt')
    model = request.data.get('model', 'llama3.2')
    system_prompt = request.data.get('system', "You are a helpful chat assistant.")
    
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        return Response(response.json())
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

