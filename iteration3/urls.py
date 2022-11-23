from django.urls import path, include
from iteration3 import views
urlpatterns = [
    path('', views.index),
    # path('auth/', include('social_django.urls', namespace='social')),
    path('login/', views.login, name='login'),
    path('index/', views.index, name='index'),
    path('guide/', views.guide, name='guide'),
    path('diary/', views.diary, name='diary'),
    path('ajax/load_portion/', views.load_portion, name='ajax_load_portion'),
    path('ajax/load_cart/', views.load_cart, name='ajax_load_cart'),
    path('ajax/load_description/', views.load_description, name='ajax_load_description'),
    path('create_view/', views.create_view, name='create_view'),
    path('history/', views.history, name='history'),
    path('entry_view/', views.entry_view, name='entry_view'),
    path('please_login/', views.please_login, name='please_login'),
    path('add_list/', views.add_list, name='add_list'),
    path('metrics/', views.metrics, name='metrics'),
    path('faq/', views.FAQ, name='FAQ'),
    path('tips/', views.tips, name='tips'),
    path('mail/', views.email_form, name='mail'),
    path('success/', views.success, name='success'),
    path('logout/', views.logout, name='logout'),
]