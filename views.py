
# views.py - مرحله چهارم: نمایش و ذخیره فرم رأی‌گیری
from django.shortcuts import render, redirect
from .forms import User, VoteForm, VoteAnswerForm
from .models import Vote, VoteAnswer
from django.contrib import messages
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import TeacherForm
from django.http import JsonResponse
from .forms import RegisterForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.views import PasswordResetCompleteView
from django.contrib.auth.models import Group
from .forms import LoginForm
from .models import Teacher
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q

failed_attempts = {}  # دیکشنری برای ثبت تعداد تلاش‌ها

def password_reset_offline(request):
    global failed_attempts
    error_message = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        key = f'{username}:{email}'

        if failed_attempts.get(key, 0) >= 3:
            error_message = 'تعداد تلاش‌های ناموفق بیش از حد مجاز است. لطفاً یک ساعت دیگر دوباره تلاش کنید.'
        else:
            try:
                user = User.objects.get(Q(username=username) & Q(email=email))
                # اگر پیدا شد هدایت به صفحه تنظیم رمز
                return redirect('password_reset_confirm', uidb64='dummy', token='set-password')  # مسیر ساختگی
            except User.DoesNotExist:
                failed_attempts[key] = failed_attempts.get(key, 0) + 1
                error_message = 'نام کاربری یا ایمیل مطابقت ندارد.'
    return render(request, 'registration/password_reset_form.html', {'error_message': error_message})

def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if user.is_superuser:
                return redirect('admin_dashboard')
            else:
                return redirect('student_dashboard')
        else:
            messages.error(request, 'نام کاربری یا رمز عبور اشتباه است.')
    return render(request, 'registration/login.html')

def password_reset(request):
    return render(request, 'password_reset_form.html')

def register_limited_manager(request):
    if User.objects.filter(groups__name='LimitedManager').exists():
        return HttpResponse("مدیر محدود قبلاً ایجاد شده است.")      
def is_limited_manager(user):
    return user.groups.filter(name='LimitedManager').exists()

@login_required
@user_passes_test(is_limited_manager)
def manager_dashboard(request):
   return render(request, 'survey/vote_form.html')
    # صفحه مدیریت محدود

def vote_form(request):
    if request.method == 'POST':
        vote_form = VoteForm(request.POST)
        answer_form = VoteAnswerForm(request.POST)
        if vote_form.is_valid() and answer_form.is_valid():
            vote = vote_form.save(commit=False)
            vote.voter = request.user
            vote.save()
            for i in range(1, 15):
                ans = answer_form.cleaned_data[f'q{i}']
                VoteAnswer.objects.create(vote=vote, question_number=i, answer=ans)
            messages.success(request, "رأی شما موفقانه ثبت شد.")
            return redirect('vote')
    else:
        vote_form = VoteForm()
        answer_form = VoteAnswerForm()

    return render(request, 'survey/vote_form.html', {
        'vote_form': vote_form,
        'answer_form': answer_form,
    })

def home(request):
    return render(request, 'survey/home.html')

# مرحله ششم: تحلیل نتایج و نمایش درصد رأی مثبت هر سوال
# فایل: survey/views.py (ادامه یا انتهای فایل اضافه شود)



def vote_results(request):
    teachers = Teacher.objects.all()
    selected_teacher_id = request.GET.get('teacher')
    chart_data = []
    selected_teacher = None

    if selected_teacher_id:
        selected_teacher = Teacher.objects.get(id=selected_teacher_id)
        votes = Vote.objects.filter(teacher=selected_teacher)
        total_votes = votes.count()

        if total_votes > 0:
            for i in range(1, 15):
                count = VoteAnswer.objects.filter(
                    vote__teacher=selected_teacher,
                    question_number=i,
                    answer="بلی"
                ).count()
                percent = round((count / total_votes) * 100, 1)
                chart_data.append({"question": f"سوال {i}", "percent": percent})

    return render(request, 'survey/results.html', {
        'teachers': teachers,
        'selected_teacher': selected_teacher,
        'chart_data': chart_data,
    })

# ادامه views.py برای ساخت PDF از تحلیل رأی‌ها

def generate_pdf(request):
    if request.method == 'POST':
        teacher_id = request.POST.get('teacher_id')
        teacher = Teacher.objects.get(id=teacher_id)
        votes = Vote.objects.filter(teacher=teacher)
        total_votes = votes.count()

        buffer = BytesIO()
        pdf = canvas.Canvas(buffer)

        pdf.setFont("Helvetica", 12)
        pdf.drawString(100, 800, f"گزارش رأی‌گیری استاد: {teacher.first_name} {teacher.last_name}")
        pdf.drawString(100, 780, f"تاریخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        pdf.drawString(100, 760, f"تعداد کل رأی‌ها: {total_votes}")

        y = 740
        for i in range(1, 15):
            count = VoteAnswer.objects.filter(
                vote__teacher=teacher,
                question_number=i,
                answer="بلی"
            ).count()
            percent = round((count / total_votes) * 100, 1) if total_votes > 0 else 0
            pdf.drawString(100, y, f"سوال {i}: {percent}% رأی مثبت")
            y -= 20

        pdf.showPage()
        pdf.save()
        buffer.seek(0)

        filename = f"vote_report_{teacher.last_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

# views.py - ویو ثبت استاد فقط برای مدیر

# بررسی اینکه آیا کاربر مدیر است یا نه
def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def add_teacher(request):
    if request.method == 'POST':
        form = TeacherForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('teacher_added')
    else:
        form = TeacherForm()

    return render(request, 'survey/add_teacher.html', {'form': form})

def teacher_added(request):
    return render(request, 'survey/teacher_added.html')
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return JsonResponse({'success': True, 'redirect_url': '/dashboard/'})
        else:
            errors = [str(err) for err in form.errors.values()]
            return JsonResponse({'success': False, 'errors': errors})
    else:
        form = RegisterForm()
    return render(request,'registration/register.html', {'form': form})
def register(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        form = CustomRegisterForm(request.POST) # type: ignore
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'ثبت‌نام موفقانه انجام شد!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = CustomRegisterForm() # type: ignore
        return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = authenticate(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password']
        )

        if user is not None:
            login(request, user)
            return render('dashboar:home')
        else:
            form.add_error(None, "نام کاربری یا رمز عبور اشتباه است.")
            return render(request, 'registration/login.html', {'form': form})
            # تغییر مسیر بر اساس نقش کاربر
            if user.profile.role == 'admin':
                return JsonResponse({'success': True, 'redirect_url': '/admin_dashboard/'})
            else:
                return JsonResponse({'success': True, 'redirect_url': '/student_dashboard/'})

class CustomPasswordResetView(PasswordResetView):
    template_name = 'password_reset.html'
    email_template_name = 'password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'password_reset_confirm.html'
    success_url = reverse_lazy('login')  # یا صفحه موفقیت سفارشی
class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'registration/password_reset_complete.html'
    


