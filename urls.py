from django.urls import path
from .import views
from .views import register_view
from .views import login_view
from .views import CustomPasswordResetView
from .views import CustomPasswordResetConfirmView
from .views import CustomPasswordResetCompleteView
from django.contrib.auth import views as auth_views

app_name ='survey'

urlpatterns = [

    path('', views.home,name='home'),
    path('vote/', views.vote_form,name='vote'),
    path('results/', views.vote_results, name='results'),
    path('results/',views.generate_pdf,name='generate_pdf'),
    path('register/', views.register_view,name='register'),
    path('login/',  views.login_view , name='login'),
    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/', views.password_reset, name='password_reset'),
    path ('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html'
    ), name='password_reset'),
    
]

urlpatterns += [
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
urlpatterns += [
    path('reset/done/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

