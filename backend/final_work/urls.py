"""final_work URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
# URL和函数的对应关系


from django.contrib import admin
from django.urls import path
from django.urls import re_path
from prometheus_app.views import PrometheusView 
from log_app.views import logView
from trace_app.views import traceView

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^.*\/metric$', PrometheusView.query_prometheus_data, name='prometheus'),
    re_path(r'^.*\/log$', logView.query_log_data, name='log'),
    re_path(r'^.*\/trace$', traceView.query_trace_data, name='trace'),
]
