from django.conf.urls import patterns, url
from carpool import views

urlpatterns = [
        url(r'^$', views.index, name='index'),
        url(r'^aboutus/$', views.aboutus, name='aboutus'),
        url(r'^register/$', views.register, name='register'),
        url(r'^login/$', views.user_login,name='login'),
        url(r'^logout/$', views.user_logout,name='logout'),
        url(r'^nopermission/$', views.nopermission,name='nopermission'),
        url(r'^verification/$', views.verification, name='verification'),
        url(r'^newsfeed/$', views.newsfeed, name='newsfeed'),
        url(r'^profile/(?P<user_id>[0-9]+)/$', views.profile, name='profile'),
        url(r'^profile/(?P<user_name>\w+)/$', views.profile_by_name, name='profile_by_name'),
        url(r'^updateinfo/$', views.updateinfo, name='updateinfo'),
        url(r'^spread/(?P<post_id>[0-9]+)/$', views.spread, name='spread'),
        url(r'^post/(?P<post_id>[0-9]+)/$', views.post, name='post'),
        url(r'^block/(?P<user_id>[0-9]+)/$', views.block, name='block'),
        url(r'^unblock/(?P<user_id>[0-9]+)/$', views.unblock, name='unblock'),
        url(r'^change_password/$',views.change_password, name='change_password'),
        url(r'^cars/$', views.cars,name='cars'),
        url(r'^sharetrip/$', views.sharetrip,name='sharetrip'),
        url(r'^requestatrip/$',views.requestatrip,name='requestatrip'),
        url(r'^pendingrequests/$', views.pendingrequests,name='pendingrequests'),
        url(r'^previoustrips/$', views.previoustrips,name='previoustrips'),
        url(r'^tripapply/(?P<trip_id>[0-9]+)/(?P<seat_count>[0-9])/$',views.tripapply,name='tripapply'),
        url(r'^approve/(?P<trip_request_id>[0-9]+)/(?P<trip_id>[0-9]+)/(?P<seat_count>[0-9])/$',views.approve,name='approve'),


        ]