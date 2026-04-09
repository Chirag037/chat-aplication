from django.db import models
from django.contrib.auth.models import User

class Room(models.Model):
    ROOM_TYPES = (
        ('group', 'group'),
        ('direct', 'direct'),
    )
    name = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=10, choices=ROOM_TYPES, default='group')
    participants = models.ManyToManyField(User, related_name='rooms')

    def __str__(self):
        return self.name or f"Direct message between {self.id}"
        
class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages', null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username}: {self.content[:20]}"
