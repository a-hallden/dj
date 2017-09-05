from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.views import generic
from django.views.generic.edit import CreateView
from .models import Message, Conversation
from .forms import MessageForm, AddParticipantForm, NewConversationForm
from django.contrib.auth.models import User
from django.http import JsonResponse
from .serializers import *
from .permissions import *
from rest_framework import viewsets

# Viewsets
class UserViewSet(viewsets.ModelViewSet):
	queryset = User.objects.all()
	serializer_class = UserSerializer

class ConversationViewSet(viewsets.ModelViewSet):
	queryset = Conversation.objects.all()
	serializer_class = ConversationSerializer

class MessageViewSet(viewsets.ModelViewSet):
	queryset = Message.objects.all()
	serializer_class = MessageSerializer
	permission_classes = (IsOwnerOrReadOnly,)

	def pre_save(self, object):
		object.sent_by = self.request.user
		# Any time a message is added by a user, currently logged in user is set
		# as owner of the new message object

# Views
# All conversations
class AllConversationsView(generic.TemplateView):
	template_name = 'messenger/allconversations.html'

	def get(self, request):
		if request.user.is_authenticated():
			form = NewConversationForm()
			all_conversations = self.request.user.conversation_set.all().order_by('created')
			return render(request, self.template_name, {'form': form, 'all_conversations': all_conversations})
		else:
			return redirect('messenger:login')

	def post(self, request):
		form = NewConversationForm(request.POST)

		if form.is_valid():
			conversation = form.save()
			conversation.participants.add(self.request.user)
			conversation.save()
			return redirect('messenger:conversation', conversation.pk)

# Single conversation
class ConversationView(generic.TemplateView):
	template_name = 'messenger/conversation.html'

	def get(self, request, conversation_id):
		conversation = Conversation.objects.get(pk=conversation_id)
		participants = conversation.participants.all()
		messages = conversation.message_set.all().order_by('timestamp')
		messageform = MessageForm()
		participantform = AddParticipantForm()
		return render(request, 'messenger/conversation.html',
			{'messageform': messageform, 'participantform': participantform, 'conversation': conversation, 'participants': participants, 'messages': messages, 'pk': conversation_id})

	def post(self, request, conversation_id):
		form = MessageForm(request.POST)

		if form.is_valid():
			message = form.save(commit=False)
			message.conversation = Conversation.objects.get(pk=conversation_id)
			message.sent_by = self.request.user
			message.save()
			return redirect('messenger:conversation', conversation_id)

# New conversation
class NewConversationView(generic.TemplateView):
	template_name = 'messenger/newconversation.html'

	def get(self, request):
		form = NewConversationForm()
		return render(request, self.template_name, {'form': form})

	def post(self, request):
		form = NewConversationForm(request.POST)

		if form.is_valid():
			conversation = form.save()
			conversation.participants.add(self.request.user)
			conversation.save()
			return redirect('messenger:conversation', conversation.pk)

# Add participants to a conversation
class AddParticipantView(generic.TemplateView):
	template_name = 'messenger/addparticipant.html'

	def get(self, request, conversation_id):
		form = AddParticipantForm()
		conversation = get_object_or_404(Conversation, pk=conversation_id)
		return render(request, self.template_name, {'form': form, 'conversation': conversation})

	def post(self, request, conversation_id):
		form = AddParticipantForm(request.POST)
		conversation = get_object_or_404(Conversation, pk=conversation_id)

		if form.is_valid():
			username = form.cleaned_data['username']
			try:
				user = User.objects.get(username=username)
			except User.DoesNotExist:
				form = AddParticipantForm()
				return render(request, self.template_name,
					{'form': form, 'conversation': conversation, 'error': ('User ' + username + ' does not exist!')})

			conversation.participants.add(user)
			conversation.save()
			return redirect('messenger:conversation', conversation.pk)

		else:
			return render(request, 'messenger/error.html', {'error': 'something went terribly wrong'})

# Edit message
class EditMessageView(generic.TemplateView):
	template_name = 'messenger/editmessage.html'

	def get(self, request, message_id):
		message = get_object_or_404(Message, pk=message_id)

		if is_owner(request, message_id):
			form = MessageForm()
			return render(request, self.template_name, {'form': form})
		else:
			return render(request, 'messenger/error.html', {'error': 'You cannot edit messages that aren\'t yours.'})

	def post(self, request, message_id):
		message = get_object_or_404(Message, pk=message_id)
		conversation = message.conversation
		form = MessageForm(request.POST)

		if form.is_valid():
			message.message_text = request.POST['message_text']
			message.save()
			return redirect('messenger:conversation', conversation.pk)

def leave_conversation(request, conversation_id):
	conversation = Conversation.objects.get(pk=conversation_id)

	if conversation.participants.all().count() == 1: # If the user is the only one in the conversation, delete whole conversation
		conversation.delete()
	else:
		request.user.conversation_set.remove(conversation) # Otherwise just remove the user

	return redirect('messenger:conversations')

# Removes a message
def remove_message(request, message_id):
	message = get_object_or_404(Message, pk=message_id)
	conversation = message.conversation

	if is_owner(request, message_id):
		message.delete()
	else:
		return render(request, 'messenger/error.html', {'error': 'You cannot delete messages that aren\'t yours.'})

	return redirect('messenger:conversation', conversation.pk)

# Registers a new user and logs in
def register(request):
	if request.method == 'POST':
		form = UserCreationForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password2')
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				return redirect('messenger:conversations')
	else:
		form = UserCreationForm()

	return render(request, 'messenger/register.html', {'form': form})

# Helper methods
def validate_username(request):
	username = request.GET.get('username', None)
	data = {
		'is_taken': User.objects.filter(username__iexact=username).exists()
	}
	if data['is_taken']:
		data['error_message'] = "That username is already taken!"
	return JsonResponse(data)

def is_owner(request, message_id):
	return request.user == Message.objects.get(pk=message_id).sent_by
