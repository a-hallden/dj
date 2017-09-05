from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(prefix='conversation', viewset=views.ConversationViewSet)
router.register(prefix='message', viewset=views.MessageViewSet)
router.register(prefix='user', viewset=views.UserViewSet)

app_name = 'messenger'
urlpatterns = [
	# Account handling
	url(r'^register/$', views.register, name='register'),
	url(r'^ajax/validate_username/$', views.validate_username, name='validate_username'),
	url(r'^login/$', auth_views.login, {'template_name': 'messenger/login.html'}, name='login'),
	url(r'^logout/$', auth_views.logout, {'next_page': 'messenger:conversations'}, name='logout'),

	# Conversation handling
	url(r'^$', views.AllConversationsView.as_view(), name='conversations'),
	url(r'^conversations/(?P<conversation_id>[0-9]+)/$', views.ConversationView.as_view(), name="conversation"),
	url(r'^newconversation/$', views.NewConversationView.as_view(), name="newconversation"),

	# Message handling
	url(r'^leaveconversation/(?P<conversation_id>[0-9]+)/$', views.leave_conversation, name="leaveconversation"),
	url(r'^addparticipant/(?P<conversation_id>[0-9]+)/$', views.AddParticipantView.as_view(), name="addparticipant"),
	url(r'^removemessage/(?P<message_id>[0-9]+)/$', views.remove_message, name="removemessage"),
	url(r'^editmessage/(?P<message_id>[0-9]+)/$', views.EditMessageView.as_view(), name="editmessage"),
]
urlpatterns += router.urls
