from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.db.models import Count

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
    STATUS_CHOICES = (
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('viewed', 'Viewed'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages', null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='sent')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username}: {self.content[:20]}"


class MessageRead(models.Model):
    """Per-user read receipt for a message (used in group rooms)."""
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reads')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_reads')
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['read_at']
        constraints = [
            models.UniqueConstraint(fields=['message', 'user'], name='unique_message_read_per_user'),
        ]

    def __str__(self):
        return f"{self.user.username} read msg {self.message_id}"


@receiver(post_delete, sender=User)
def cleanup_orphaned_rooms(sender, instance, **kwargs):
    """Delete any direct rooms that now have fewer than 2 participants."""
    orphaned_rooms = Room.objects.filter(type='direct').annotate(p_count=Count('participants')).filter(p_count__lt=2)
    orphaned_rooms.delete()
