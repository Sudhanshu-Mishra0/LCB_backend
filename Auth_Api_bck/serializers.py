from rest_framework import serializers
from django.core.mail import send_mail
from django.conf import settings
from .models import User, TrainerProfile, CounsellorProfile, StudentProfile, AdminProfile, Batch

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'password', 'confirm_password']

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords don't match."})
        return attrs

    def create(self, validated_data):
        user = User(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            phone_number=validated_data['phone_number'],
            is_active=False  # Set inactive until verified
        )
        user.set_password(validated_data['password'])
        user.save()
        user.generate_otp()  # Generate OTP
        send_mail(
            'Your OTP Code',
            f'Your OTP code is: {user.otp}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ['middle_name', 'age', 'gender', 'contact_info', 'address', 'dob', 'user', 'user__profile_picture']

class BatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = ['course', 'trainer', 'start_date', 'end_date', 'capacity', 'current_enrollment']

class TrainerProfileSerializer(serializers.ModelSerializer):
    batches = serializers.PrimaryKeyRelatedField(many=True, queryset=Batch.objects.all())  # Link to Batch
    class Meta:
        model = TrainerProfile
        fields = ['middle_name', 'expertise', 'subject_taught', 'contact_info', 'date_joined', 'added_by', 'user', 'user__profile_picture', 'batches']


class CounsellorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CounsellorProfile
        fields = ['middle_name', 'short_profile_summary', 'contact_info', 'date_joined', 'added_by', 'user', 'user__profile_picture']

class AdminProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminProfile
        fields = ['middle_name', 'user', 'user__profile_picture', 'date_joined']
