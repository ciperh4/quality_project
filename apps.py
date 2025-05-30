from django.apps import AppConfig
from django.db.models.signals import post_migrate

class SurveyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'survey'

def create_roles(sender, **kwargs):
    from django.contrib.auth.models import Group, Permission
    from django.contrib.contenttypes.models import ContentType
    from .models import Teacher, Employee  # مدل‌هایی که باید مدیر کنترل کنه

    # ایجاد گروه محدود
    group, created = Group.objects.get_or_create(name='LimitedManager')

    # دسترسی‌هایی که باید داشته باشه
    perms = [
        'add_teacher', 'change_teacher', 'delete_teacher',
        'add_employee', 'change_employee', 'delete_employee',
        'view_vote', 'view_student'
    ]
    for perm_code in perms:
        try:
            perm = Permission.objects.get(codename=perm_code)
            group.permissions.add(perm)
        except:
            continue

class YourAppConfig(AppConfig):
    name = 'your_app_name'

    def ready(self):
        post_migrate.connect(create_roles, sender=self)
