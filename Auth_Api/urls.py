from django.urls import path
from .views import *


urlpatterns = [
    path('home/', HomePageView.as_view(), name='home-page'),
    path('register-student/', StudentRegistrationView.as_view(), name='register-student'),
    path('register-trainer/', TrainerProfileView.as_view(), name='register-trainer'),
    path('register-counsellor/', CounsellorProfileView.as_view(), name='register-counsellor'),
    path('verify-otp/', VerifyOtpView.as_view(), name='verify-otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),    
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('dashboard/student/', StudentDashboardView.as_view(), name='student-dashboard'),
    path('dashboard/trainer/', TrainerDashboardView.as_view(), name='trainer-dashboard'),
    path('dashboard/counsellor/', CounsellorDashboardView.as_view(), name='counsellor-dashboard'),
    path('trainers_profile/', TrainerProfileView.as_view(), name='trainers_profile'),
    path('counsellors_profile/', CounsellorProfileView.as_view(), name='counsellors_profile'),
]