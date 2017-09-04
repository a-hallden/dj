from django import forms
from .models import Conversation, Message
from django.contrib.auth.models import User


class MessageForm(forms.ModelForm):
	class Meta:
		model = Message
		fields = ('message_text',)
		widgets = {'message_text': forms.Textarea(attrs={'rows': 4})}

class NewConversationForm(forms.ModelForm):
	conversation_name = forms.CharField(max_length=100)

	class Meta:
		model = Conversation
		fields = ('conversation_name',)

class AddParticipantForm(forms.Form):
	username = forms.CharField(max_length=150)

	class Meta:
		fields = ('username',)
