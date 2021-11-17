"""cas URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.models import Group
from django.urls import include, path

from account.views import google_login

admin.site.unregister(Group)
admin.site.site_header = 'Central Authentication Service'
admin.site.site_title = 'Central Authentication Service'

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'', include('mama_cas.urls')),
    url(r'^google-login/$', google_login, name="google-login"),
]
