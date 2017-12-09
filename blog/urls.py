# -*- coding:utf-8 -*-
#  made in ly
from django.conf.urls import url
from .import views

app_name = 'blog'
urlpatterns = [
    url(r'^$',views.IndexView.as_view(), name="index"),
    url(r'^post/(?P<pk>[0-9]+)/$', views.PostDetailView.as_view(), name='detail'),
    url(r'^in_time/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})/$',views.In_TimeView.as_view(), name="in_time"),
    url(r'^category/(?P<pk>[0-9]+)/$', views.CategoryView.as_view(), name="category"),
    url(r'^tag_cloud/(?P<pk>[0-9]+)/$', views.Tag_CloudView.as_view(), name='tag_cloud'),
#    url(r'^to_author/(?P<author>[0-9]+)/$',views.To_authorView.as_view(), name = 'to_author'),

]