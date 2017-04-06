"""TakeMyMoney URL Configuration

The `urlpatterns` list routes URLs to  For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

from TakeMyMoney.views import project_display, project_update, pledging, authentication, authorization, user_display, logging

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^$', project_display.project_list),
    url(r'^projectList/', project_display.project_list),
    url(r'^projectDetails/', project_display.project_details),

    url(r'^addNewProject/', project_update.add_new_project),
    url(r'^editProject/', project_update.edit_project),
    url(r'^storeProject/', project_update.store_project),
    url(r'^updateProject/', project_update.update_project),
    url(r'^deleteProject/', project_update.delete_project),

    url(r'^addFunding/', pledging.add_funding),
    url(r'^storeFunding/', pledging.store_funding),

    url(r'^login/', authentication.login),
    url(r'^attemptLogin/', authentication.attempt_login),
    url(r'^signUp/', authentication.add_new_user),
    url(r'^storeUser/', authentication.store_user),
    url(r'^signOut/', authentication.logout),

    url(r'^userList/', user_display.user_list),
    url(r'^userDetails/', user_display.user_details),
    
    url(r'^makeAdmin/', authorization.make_admin),
    url(r'^revokeAdmin/', authorization.revoke_admin),

    url(r'^projectsLog/', logging.projects_log),
    url(r'^roleLog/', logging.role_log)
]
