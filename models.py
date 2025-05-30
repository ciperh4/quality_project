from django.db import models
# models.py - مدل‌های دیتابیس برای رأی‌دهی سیستم تضمین کیفیت
from django.db import models
from django.contrib.auth.models import User

# نقش‌های کاربر برای مدیریت سطح دسترسی
class Profile(models.Model):
    ROLE_CHOICES = [
        ('student', 'محصل'),
        ('teacher', 'استاد'),
        ('admin', 'مدیر'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

# مدل استاد
class Teacher(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    department = models.CharField(max_length=100)
    faculty = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

# مدل رأی که هر محصل برای یک استاد ثبت می‌کند
class Vote(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    voter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    subject = models.CharField(max_length=100)
    semester = models.CharField(max_length=10)
    class_name = models.CharField(max_length=50)
    vote_date = models.DateField(auto_now_add=True)
    comment = models.TextField(blank=True)

    def __str__(self):
        return f"رأی برای {self.teacher} در {self.subject}"

# مدل پاسخ به سوالات رأی‌گیری (14 سوال)
class VoteAnswer(models.Model):
    vote = models.ForeignKey(Vote, on_delete=models.CASCADE, related_name='answers')
    question_number = models.PositiveSmallIntegerField()
    answer = models.CharField(max_length=10)  # بلی، نخیر، نسبتا

    def __str__(self):
        return f"سوال {self.question_number} - {self.answer}"
# Create your models here.
