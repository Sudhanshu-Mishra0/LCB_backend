from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from django.utils import timezone
from datetime import timedelta
from .serializers import *
from .models import *
from .utils.email import send_otp_email, send_new_otp_email, send_password_reset_otp_email
from .utils.messages import *



def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class HomePageView(APIView):
    def get(self, request):
        # Return a simple welcome message
        response_data = {
            "message": "Welcome to the Home Page!"
        }
        return Response(response_data, status=status.HTTP_200_OK)

class StudentRegistrationView(APIView):
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.generate_otp()  # Generate OTP
            send_otp_email(user.email, user.otp)  # Send OTP email
            return Response({"message": USER_REGISTERED_SUCCESSFULLY}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        users = User.objects.filter(role='student')  # Filter for students
        serializer = RegistrationSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class VerifyOtpView(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        try:
            user = User.objects.get(email=email)
            if user.otp == otp and user.otp_created_at > timezone.now() - timedelta(minutes=5):
                user.is_verified = True
                user.is_active = True
                user.otp = None
                user.otp_created_at = None
                user.save()
                return Response({"message": OTP_VERIFIED_SUCCESSFULLY}, status=status.HTTP_200_OK)
            else:
                return self.regenerate_otp(user)  # Regenerate OTP if invalid or expired
        except User.DoesNotExist:
            return Response({"error": USER_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
    def regenerate_otp(self, user):
        user.generate_otp()  # Generate a new OTP
        send_new_otp_email(user.email, user.otp)  # Send new OTP email
        return Response({"message": OTP_EXPIRED_MESSAGE}, status=status.HTTP_200_OK)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(email=email, password=password)
            if user:
                if not user.is_verified:
                    return Response({"error": ACCOUNT_INACTIVE}, status=status.HTTP_403_FORBIDDEN)
                tokens = get_tokens_for_user(user)  # Generate tokens
                return Response({
                    "tokens": tokens,
                    "message": LOGIN_SUCCESSFUL
                }, status=status.HTTP_200_OK)
            return Response({"error": INVALID_CREDENTIALS}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TrainerProfileView(APIView):
    permission_classes = [IsAdminUser]  # Only admins can access this view
    def post(self, request):
        serializer = TrainerProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": TRAINER_REGISTERED_SUCCESSFULLY}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        trainers = TrainerProfile.objects.all()
        serializer = TrainerProfileSerializer(trainers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CounsellorProfileView(APIView):
    permission_classes = [IsAdminUser]  # Only admins can access this view
    def post(self, request):
        serializer = CounsellorProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": COUNSELLOR_REGISTERED_SUCCESSFULLY}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        counsellors = CounsellorProfile.objects.all()
        serializer = CounsellorProfileSerializer(counsellors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class LogoutView(APIView):
    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({"error": REFRESH_TOKEN_REQUIRED}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # Blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": LOGOUT_SUCCESSFUL}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": INVALID_REFRESH_TOKEN}, status=status.HTTP_401_UNAUTHORIZED)

class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            user.generate_otp()  # Generate OTP for password reset
            send_password_reset_otp_email(user.email, user.otp)  # Send OTP email
            return Response({"message": "Password reset OTP has been sent."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
class ResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')
        try:
            user = User.objects.get(email=email)
            if user.otp == otp and user.otp_created_at > timezone.now() - timedelta(minutes=5):
                user.set_password(new_password)  # Set the new password
                user.otp = None  # Clear the OTP after use
                user.otp_created_at = None
                user.save()
                return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")
        confirm_new_password = request.data.get("confirm_new_password")

        if user.check_password(current_password):
            if new_password == confirm_new_password:
                user.set_password(new_password)
                user.save()
                return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "New password and confirmation do not match."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "Current password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)


class StudentDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        try:
            student_profile = StudentProfile.objects.get(user=user)
            enrollments = Enrollment.objects.filter(student=user)
            courses = [enrollment.course.title for enrollment in enrollments]

            response_data = {
                "student_profile": StudentProfileSerializer(student_profile).data,
                "enrolled_courses": courses,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except StudentProfile.DoesNotExist:
            return Response({"error": "Student profile not found."}, status=status.HTTP_404_NOT_FOUND)


class TrainerDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        try:
            trainer_profile = TrainerProfile.objects.get(user=user)
            batches = trainer_profile.batches.all()
            students = [enrollment.student.email for batch in batches for enrollment in Enrollment.objects.filter(course=batch.course)]

            response_data = {
                "trainer_profile": TrainerProfileSerializer(trainer_profile).data,
                "batches": BatchSerializer(batches, many=True).data,
                "assigned_students": students,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except TrainerProfile.DoesNotExist:
            return Response({"error": "Trainer profile not found."}, status=status.HTTP_404_NOT_FOUND)



class CounsellorDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        try:
            counsellor_profile = CounsellorProfile.objects.get(user=user)
            students = User.objects.filter(role='student')  # Fetch all students or filter by counselling relationship

            response_data = {
                "counsellor_profile": CounsellorProfileSerializer(counsellor_profile).data,
                "students": [student.email for student in students],
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except CounsellorProfile.DoesNotExist:
            return Response({"error": "Counsellor profile not found."}, status=status.HTTP_404_NOT_FOUND)

