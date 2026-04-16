from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Room, Message

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class RoomSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    
    class Meta:
        model = Room
        fields = ['id', 'name', 'type', 'participants']

class MessageSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    seen_by = serializers.SerializerMethodField()
    room_type = serializers.CharField(source='room.type', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'user', 'username', 'content', 'room', 'status', 'created_at', 'seen_by', 'room_type', 'message_type', 'attachment']

    def get_seen_by(self, obj):
        if not obj.room or obj.room.type != 'group':
            return []
        return list(
            obj.reads.values_list('user__username', flat=True).order_by('read_at')
        )
