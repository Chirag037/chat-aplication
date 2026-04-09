from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Message, Room
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, RoomSerializer, MessageSerializer

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
    # Returns only direct message rooms for the current user
    rooms = Room.objects.filter(participants=request.user, type='direct')
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

        msgs = Message.objects.filter(room=room).select_related('user')
        serializer = MessageSerializer(msgs, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        content = request.data.get('content')
        room_id = request.data.get('room')
        
        if not content or not room_id or room_id == 'null':
            return Response({"error": "content and room are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            room = Room.objects.get(id=room_id, participants=request.user)
        except Room.DoesNotExist:
            return Response({"error": "Room not found or access denied"}, status=status.HTTP_403_FORBIDDEN)

        msg = Message.objects.create(user=request.user, content=content, room=room)
        serializer = MessageSerializer(msg)
        return Response(serializer.data, status=status.HTTP_201_CREATED)