# مرحله سوم: فرم رأی‌گیری و ویو برای ذخیره رأی‌ها
# فایل: survey/forms.py
from django import forms
from .models import Teacher, Vote, VoteAnswer
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class VoteForm(forms.ModelForm):
    class Meta:
        model = Vote
        fields = ['teacher', 'subject', 'semester', 'class_name', 'comment']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teacher'].label = "استاد"
        self.fields['subject'].label = "مضمون"
        self.fields['semester'].label = "سمستر"
        self.fields['class_name'].label = "صنف"
        self.fields['comment'].label = "نظریات شما (اختیاری)"


class VoteAnswerForm(forms.Form):
    CHOICES = [("بلی", "بلی"), ("نسبتا", "نسبتا"), ("نخیر", "نخیر")]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        questions = [
            "آیا در آغاز سمستر کورس پالیسی توسط استاد تشریح شد؟",
            "آیا تدریس مطابق کورس پالیسی مضمون صورت گرفت؟",
            "آیا مواد درسی معرفی شده و موجود است؟",
            "آیا تدریس استاد قابل فهم است؟",
            "آیا از شیوه تدریس استاد راضی هستید؟",
            "آیا استاد محصلان را در تدریس سهیم می‌سازد؟",
            "آیا از برخورد اکادمیک استاد راضی هستید؟",
            "آیا استاد با پلان درسی منظم داخل صنف می‌شود؟",
            "آیا استاد به سوالات پاسخ قناعت‌بخش می‌دهد؟",
            "آیا استاد به وقت پایبند است؟",
            "آیا استاد بیشتر به موضوعات غیرمرتبط می‌پردازد؟",
            "آیا مشکلات درسی شما توسط استاد حل می‌شود؟",
            "آیا از شیوه‌های ارزیابی استاد راضی هستید؟",
            "آیا استاد از تکنالوژی معلوماتی استفاده می‌کند؟"
        ]
        for i, q in enumerate(questions):
            self.fields[f'q{i+1}'] = forms.ChoiceField(
                label=q,
                choices=self.CHOICES,
                widget=forms.RadioSelect,
                required=True
            )
class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['first_name', 'last_name', 'faculty', 'department']
        labels = {
            'first_name': 'نام',
            'last_name': 'تخلص',
            'faculty': 'پوهنحی',
            'department': 'دیپارتمنت',
        }
class RegisterForm(UserCreationForm):
    full_name = forms.CharField(max_length=150,required=True,label='نام کامل')
    class Meta:
        model = User
        fields = ['username','email','password1','password2',]
        labels ={'username': 'نام کاربری',
                 'email':'ایمیل',
                 'password1':'رمز عبور',
                 'password2':'تکرار رمز عبور',
                 }
        def save(self, commit=True):
            User = super().save(commit=False)
            User.email = self.cleaned_data['email']
            User.first_name = self.cleaned_data['full_name']
            if commit:
                User.save()
                return User
class CustomRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','email','password1','password2',]
        labels ={'username': 'نام کاربری',
                 'email':'ایمیل',
                 'password1':'رمز عبور',
                 'password2':'تکرار رمز عبور',
        }
        help_texts ={
            'username': '',
            'email': '',
            'password1': '',
            'password2': '',
            
        }
   
    email = forms.EmailField(required=True)
class LoginForm(forms.Form):
    username = forms.CharField(label='نام کاربر', max_length=100)
    password = forms.CharField(label='رمز عبور', widget=forms.PasswordInput)   
    