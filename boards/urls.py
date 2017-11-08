from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.BoardList.as_view(), name='board_list'),
    url(r'^(?P<category_slug>[-\w]+)/$', views.BoardListByCategory.as_view(), name='board_list_by_category'),
    url(r'^(?P<pk>\d+)/(?P<slug>[-\w]+)/$', views.BoardDetail.as_view(), name='board_detail'),
]