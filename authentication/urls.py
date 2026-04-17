from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, MeView, ChangePasswordView, PendingUsersView, ApproveUserView, UsersListView, UserManageView

urlpatterns = [
    path('register/',           RegisterView.as_view(),      name='auth-register'),
    path('login/',              TokenObtainPairView.as_view(), name='auth-login'),
    path('token/refresh/',      TokenRefreshView.as_view(),  name='auth-token-refresh'),
    path('me/',                 MeView.as_view(),             name='auth-me'),
    path('change-password/',    ChangePasswordView.as_view(), name='auth-change-password'),
    path('users/',              UsersListView.as_view(),      name='auth-users-list'),
    path('users/pending/',      PendingUsersView.as_view(),   name='auth-users-pending'),
    path('users/<int:pk>/approve/', ApproveUserView.as_view(), name='auth-user-approve'),
    path('users/<int:pk>/',     UserManageView.as_view(),     name='auth-user-manage'),
]
