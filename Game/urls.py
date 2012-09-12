from django.conf.urls import patterns, include, url
from main.views import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
	(r'^registration/$', registration_form),
	(r'^registration_action/$', registration),
	(r'^login/$', login),
	(r'^logout/$', logout),
	(r'^char/$', char),
	(r'^field/$', place, {'type': 'field'}),
	(r'^mine/$', place, {'type': 'mine'}),
	(r'^workshop/$', place, {'type': 'workshop'}),
	(r'^garden/$', place, {'type': 'garden'}),
	(r'^temple/$', place, {'type': 'temple'}),
	(r'^library/$', place, {'type': 'library'}),
	(r'^mail_list/$', mail_list),
	(r'^enemy_list/$', enemy_list),
	#(r'^sp_list/$', sparring_partner_list),
	(r'^fight/$', fight),
	(r'^dismiss/$', dismiss),
	(r'^attack/$', attack),
	(r'^build/(mine|workshop|garden|temple|library)/$', build),
	(r'^improve/(field|mine|workshop|garden|temple|library)/$', improve),
	(r'^missions/$', missions),
	(r'^mission_start/$', mission_start),
	(r'^mission_end/$', mission_end),
	(r'^add_new_character/$', add_new_character),
	(r'^test/', test),
	(r'^style_(\d{1,4})_(\d{1,4}).css$', get_style),
	
	(r'^$', start),
	
	# http://stackoverflow.com/questions/1129462/specifying-static-images-directory-path-in-django
	# На продакшене надо убрать
	(r'^imgs/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'imgs\\'}),
	(r'^styles/(?P<path>.*\.css)$', 'django.views.static.serve', {'document_root': 'styles\\'}),
	
    # Examples:
    # url(r'^$', 'Game.views.home', name='home'),
    # url(r'^Game/', include('Game.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
