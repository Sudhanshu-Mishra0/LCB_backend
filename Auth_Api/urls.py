from django.urls import path
from .views import *


urlpatterns = [
    path('register-student/', StudentRegistrationView.as_view(), name='register-student'),
    path('register-trainer/', TrainerProfileView.as_view(), name='register-trainer'),
    path('register-counsellor/', CounsellorProfileView.as_view(), name='register-counsellor'),
    path('verify-otp/', VerifyOtpView.as_view(), name='verify-otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),    
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),  
]