from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import random
from django.utils import timezone
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, phone_number, password=None):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, phone_number=phone_number)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, first_name, last_name, phone_number, password=None):
        user = self.create_user(email, first_name, last_name, phone_number, password)
        user.is_staff = True
        user.is_superuser = True
        user.role = 'admin'  # Set role to admin
        user.is_active = True  # Ensure superuser is active
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('trainer', 'Trainer'),
        ('counselor', 'Counselor'),
        ('admin', 'Admin'),  # Added Admin role
    ]
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True, max_length=255)
    phone_number = models.CharField(max_length=15)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number']
    objects = UserManager()
    def __str__(self):
        return self.email
    
    def generate_otp(self):
        self.otp = str(random.randint(100000, 999999))
        self.otp_created_at = timezone.now()
        self.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Call the original save method
        # Create profile based on user role
        if self.role == 'student':
            StudentProfile.objects.get_or_create(user=self)
        elif self.role == 'trainer':
            TrainerProfile.objects.get_or_create(user=self)
        elif self.role == 'counselor':
            CounsellorProfile.objects.get_or_create(user=self)
        elif self.role == 'admin':
            AdminProfile.objects.get_or_create(user=self)

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    middle_name = models.CharField(max_length=30)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    contact_info = models.TextField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    dob = models.DateField(null=True, blank=True)

class TrainerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    middle_name = models.CharField(max_length=30, blank=True)
    expertise = models.CharField(max_length=100)
    subject_taught = models.CharField(max_length=100, blank=True)
    contact_info = models.TextField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(User, related_name='trainer_added_by', on_delete=models.SET_NULL, null=True)
    batches = models.ManyToManyField('Batch', related_name='trainers', blank=True)  # Many-to-Many relation with Batch

class CounsellorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    middle_name = models.CharField(max_length=30, blank=True)
    short_profile_summary = models.TextField(null=True, blank=True)
    contact_info = models.TextField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(User, related_name='counsellor_added_by', on_delete=models.SET_NULL, null=True)

class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    middle_name = models.CharField(max_length=30, blank=True)


class Course(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    duration = models.CharField(max_length=50)  # e.g., "4 weeks", "10 hours"
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.title
    
class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('student', 'course')  # Prevent duplicate enrollments

class Batch(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    trainer = models.ForeignKey(User, on_delete=models.CASCADE)  # Assuming trainer is a User
    start_date = models.DateField()
    end_date = models.DateField()
    capacity = models.PositiveIntegerField()
    current_enrollment = models.PositiveIntegerField(default=0)
    def __str__(self):
        return f"{self.course.title} - {self.trainer.first_name} {self.trainer.last_name}"