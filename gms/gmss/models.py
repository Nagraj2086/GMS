from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings
# Create your models here.


class User(AbstractUser):
    ROLE_CHOICES=[
        ('ADMIN','Admin'),
        ('MEMBER','Member'),
    ]
    role=models.CharField(max_length=20,choices=ROLE_CHOICES,default='MEMBER')

    def __str__(self):
        return f"{self.username} ({self.role})"

class MembershipPlan(models.Model):
    name=models.CharField(max_length=100)
    duration_months=models.PositiveIntegerField()
    fee=models.DecimalField(max_digits=6,decimal_places=2)
    description=models.TextField(blank=True)
    def __str__(self):
        return f"{self.name} - {self.duration_months} months - ₹{self.fee}"


class Trainer(models.Model):
    name=models.CharField(max_length=100)
    mobile=models.CharField(max_length=15)
    specialization=models.CharField(max_length=200)
    shift_timing=models.CharField(max_length=200)

    def __str__(self):
        return f"{self.name} - {self.specialization}"


class MemberProfile(models.Model):
    GENDER_CHOICE=(
        ('MALE','Male'),
        ('FEMALE','Female'),
        ('OTHER','Other')
    )
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='member_profile')
    full_name=models.CharField(max_length=100)
    mobile=models.CharField(max_length=15)
    age=models.PositiveIntegerField(null=True,blank=True)
    gender=models.CharField(max_length=10,choices=GENDER_CHOICE,null=True,blank=True)
    address=models.TextField(blank=True)
    join_date=models.DateField(default=timezone.now)
    plan=models.ForeignKey(MembershipPlan,on_delete=models.SET_NULL,null=True,blank=True,related_name='members')
    trainer=models.ForeignKey(Trainer,on_delete=models.SET_NULL,null=True,blank=True,related_name='member')
    membership_start=models.DateField(null=True,blank=True)
    membership_end=models.DateField(null=True,blank=True)
    def __str__(self):
        return f"{self.full_name} - {self.user.username}"

class Equipment(models.Model):
    name=models.CharField(max_length=100)
    units=models.PositiveIntegerField(default=1)
    price=models.DecimalField(max_digits=8,decimal_places=2)
    purchase_date=models.DateField(default=timezone.now)
    is_active=models.BooleanField(default=True)
    def __str__(self):
        return f"{self.name} - (Units: {self.units})"


class Payment(models.Model):
    PAYMENT_MODE_CHOICE=(
        ('CASH','Cash'),
        ('ONLINE','Online'),
    )
    PAYMENT_STATUS_CHOICE=(
        ('PAID','Paid'),
        ('PENDING','Pending'),
        
    )
    member=models.ForeignKey(MemberProfile,on_delete=models.CASCADE,related_name='payments')
    plan=models.ForeignKey(MembershipPlan,on_delete=models.SET_NULL,null=True,blank=True,related_name='payments')
    amount=models.DecimalField(max_digits=8,decimal_places=2)
    payment_date=models.DateField(default=timezone.now)
    mode=models.CharField(max_length=50,choices=PAYMENT_MODE_CHOICE)
    status=models.CharField(max_length=50,choices=PAYMENT_STATUS_CHOICE,default='PENDING')
    notes=models.TextField(blank=True)
    def __str__(self):
        return f"{self.amount} - {self.member.full_name} on {self.payment_date}"


class Attendance(models.Model):
    # ATTENDANCE_STATUS=(
    #     ('PRESENT','Present'),
    #     ('ABSENT','Absent')
    # )
    member=models.ForeignKey(MemberProfile,on_delete=models.CASCADE,related_name='attendances')
    date=models.DateField(default=timezone.now)
    time_in=models.TimeField(null=True,blank=True)
    class Meta:
        unique_together=('member','date')
    # status=models.CharField(max_length=20,choices=ATTENDANCE_STATUS,default='ABSENT')
    def __str__(self):
        return f"{self.member.full_name} - {self.date} - {self.time_in}"

class Enquiry(models.Model):
    ENQUIRY_STATUS_CHOICES=(
        ('NEW','New'),
        ('SEEN','Seen'),
        ('RESOLVED','Resolved')
    )
    name=models.CharField(max_length=100)
    email=models.EmailField()
    mobile=models.CharField(max_length=15)
    message=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=20,choices=ENQUIRY_STATUS_CHOICES,default='NEW')
    def __str__(self):
        return f"Enquiry from {self.name} - {self.email} - Status: {self.status}"


class WorkoutPlan(models.Model):
    member=models.ForeignKey(MemberProfile,on_delete=models.CASCADE,related_name='workout_plans')
    title=models.CharField(max_length=100)
    description=models.TextField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True)  
    def __str__(self):
        return f"{self.title} - Created at:{self.created_at}"

class Feedback(models.Model):
    member=models.ForeignKey(MemberProfile,on_delete=models.CASCADE,related_name='feedbacks')
    message=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.member.full_name} - created at: {self.created_at}"