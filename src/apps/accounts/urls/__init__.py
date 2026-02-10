from django.urls import path
from apps.accounts.views.admin.views_auth import login_view, logout_view, post_login_redirect

# admin and agent url groups
from .admin import urlpatterns as admin_urlpatterns
from .agents import urlpatterns as agent_urlpatterns

urlpatterns = [
    # AUTH
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("post-login/", post_login_redirect, name="post-login"),
]

# extend with admin and agent URL groups
urlpatterns += admin_urlpatterns
urlpatterns += agent_urlpatterns
