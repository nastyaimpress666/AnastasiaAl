from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Application(models.Model):
    STATUS_NEW = 'new'
    STATUS_IN_WORK = 'in_work'
    STATUS_DONE = 'done'
    STATUS_CHOICES = [
        (STATUS_NEW, 'Новая'),
        (STATUS_IN_WORK, 'Принято в работу'),
        (STATUS_DONE, 'Выполнено'),
    ]

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='applications')
    plan_image = models.ImageField(upload_to='plans/')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    admin_comment = models.TextField(blank=True, null=True)
    design_image = models.ImageField(upload_to='designs/', blank=True, null=True)

    def __str__(self):
        return f'{self.title} ({self.get_status_display()})'
