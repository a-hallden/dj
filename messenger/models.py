from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Conversation(models.Model):
	participants = models.ManyToManyField(User)
	created = models.DateTimeField(auto_now=True)
	conversation_name = models.CharField(max_length=100)

	def __str__(self):
		return self.conversation_name


class Message(models.Model):
	sent_by = models.ForeignKey(User, related_name='sent_by')
	conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
	message_text = models.CharField(max_length=1000)
	timestamp = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.message_text
