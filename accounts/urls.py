from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('verify-otp/', VerifyRegistrationOtpView.as_view(), name='verify-otp'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('request-otp/', RequestOtpView.as_view(), name='request-otp'),
    path('otp_verification/', VerifyOtpView.as_view(), name='otp-verify'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('users/', UsersListview.as_view(), name='user-list'),
    path('company_profile/', CompanyProfileView.as_view(), name='comapany'),
    path('company_list/', ComapnyListView.as_view(), name='company-list'),
    path('company_review/<int:id>/', CompanyReviewView.as_view(), name='company-review'),
    path('follow/<int:user_id>/', FollowUserView.as_view(), name='follow-user'),
    path('unfollow/<int:user_id>/', UnfollowUserView.as_view(), name='unfollow-user'),
    path('followers/', FollowersListView.as_view(), name='followers-list'),
    path('following/', FollowingListView.as_view(), name='following-list'),
    path('follow_count/', FollowCountView.as_view(),name='count'),
]
