from django.urls import path
from iteration3 import views

urlpatterns = [
    # =================================== Login URLs=. ===================================
    path('please_login/', views.please_login, name='please_login'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    # path('../auth/', include('social_django.urls', namespace='social')),
    # =================================== Login URLs=. ===================================


    # =================================== Index URLs =====================================
    path('', views.index, name='index'),
    path('index/', views.index, name='index'),
    # =================================== Index URL ======================================


    # =================================== Diary URLs =====================================
    path('diary/', views.diary, name='diary'),
    path('ajax/load_description/', views.load_description, name='ajax_load_description'),
    path('ajax/load_portion/', views.load_portion, name='ajax_load_portion'),
    path('ajax/load_cart/', views.load_cart, name='ajax_load_cart'),
    path('create_view/', views.create_view, name='create_view'),
    # =================================== Diary URLs =====================================


    # =================================== History URL ====================================
    path('history/', views.history, name='history'),
    # =================================== History URL ====================================


    # =================================== Metrics URL ====================================
    path('metrics/', views.metrics, name='metrics'),
    # =================================== Metrics URL ====================================


    # =================================== Guide URLs =====================================
    path('guide/', views.guide, name='guide'),
    path('tips/', views.tips, name='tips'),
    path('faq/', views.FAQ, name='FAQ'),
    # =================================== Guide URLs =====================================


    # =================================== Mail URL =======================================
    path('mail/', views.email_form, name='mail'),
    path('success/', views.success, name='success'),
    # =================================== Mail URL =======================================


    # =================================== Unused URLs ====================================
    path('add_list/', views.add_list, name='add_list')
    # =================================== Misc URLs ======================================
]