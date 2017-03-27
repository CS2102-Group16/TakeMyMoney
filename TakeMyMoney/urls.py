"""TakeMyMoney URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

from TakeMyMoney import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^projectList/', views.project_list),
    url(r'^addNewProject/', views.add_new_project),
    url(r'^storeProject/', views.store_project),
    url(r'^$', views.project_list),

    url(r'^searchProject/', views.search_project),
    url(r'^projectDetails/', views.project_details),

    url(r'^editProject/', views.edit_project),
    url(r'^updateProject/', views.update_project),
    url(r'^deleteProject/', views.delete_project),

    url(r'^login/', views.login),

    url(r'^signUp/', views.add_new_user),
    url(r'^storeUser/', views.store_user),
    url(r'^userList/', views.user_list),
    url(r'^attemptLogin/', views.attempt_login),
    url(r'^signOut/', views.logout),

    url(r'^addFunding/', views.add_funding),
    url(r'^storeFunding/', views.store_funding),

    url(r'^userDetails/', views.user_details),
    url(r'^makeAdmin/', views.make_admin),
    url(r'^revokeAdmin/', views.revoke_admin),

    url(r'^projectsLog/', views.projects_log),
]
