from django.conf.urls import patterns, url

from fileaccess import views

urlpatterns = patterns('',
    url(r'^$', views.login_user, name='login_user'),
    url(r'^logout/', views.logout_user, name='logout_user'),
    url(r'^view_files/$', views.view_files, name='view_files'),
    url(r'^download_file/(?P<file_id>\d+)/$', views.download_file, name='download_file'),
    url(r'^delete_file/(?P<file_id>\d+)/$', views.delete_file, name='delete_file'),
    url(r'^new_file/$', views.new_file, name='new_file'),
    url(r'^edit_file/(?P<file_id>\d+)/$', views.edit_file, name='edit_file'),
)