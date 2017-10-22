from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.boards_list, name='board_list'),
    url(r'^(?P<board>[-\w]+)/$', views.board_detail, name='board_detail'),
]