from django.urls import path
from . import views

urlpatterns = [
    path("", views.aws, name="index"),
    # path("api/browser-status", views.get_browser_status, name="get_browser_status"),
    # path("api/pc-status", views.get_pc_status, name="get_pc_status"),
    path("api/browser", views.BrowserControlView.as_view(), name="browser_control"),
]
