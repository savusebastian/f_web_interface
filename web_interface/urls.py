"""web_interface URL Configuration

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
from django.contrib import admin
from django.urls import path

from pages.views import *

urlpatterns = [
	path('admin/', admin.site.urls),
	path('check_news', home_view, name='check_news'),
	path('results', results_view, name='results'),

	path('custom', custom_view, name='custom'),
	path('results_custom', results_custom_view, name='results_custom'),

	path('blackboard', blackboard_view, name='blackboard'),
	path('results_blackboard', results_blackboard_view, name='results_blackboard'),

	path('', schoolpointe_view, name='schoolpointe'),
	path('results_schoolpointe', results_schoolpointe_view, name='results_schoolpointe'),

	path('edlio_school_messenger', vpn_view, name='vpn'),
	path('files', files_view, name='files'),
]
