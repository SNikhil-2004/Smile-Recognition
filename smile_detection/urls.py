"""
URL configuration for smile_detection project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from users import views as u
from admins import views as a

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', u.home, name='home'),

    path('register/', u.register_view, name='register'),
    path('userlogin/', u.user_login, name='userlogin'),
    path('userhome/', u.user_home, name='userhome'),
    path('training/', u.training, name='training'),
    path('predictsmile/', u.predict_smile, name='predictsmile'),
    path('detect_SMILE/', u.detect_SMILE, name='detect_SMILE'),

    path('view/', a.view, name='view'),
    path('adminhome/', a.admin_home, name='adminhome'),
    path('adminlogin/', a.admin_login, name='adminlogin'),
    path('activate/<int:user_id>/', a.activate_user, name='activate'),
    path('block/<int:user_id>/', a.block_user, name='block'),
    path('delete-user/<int:user_id>/', a.delete_user, name='delete_user'),
]
