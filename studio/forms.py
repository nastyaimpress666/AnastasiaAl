from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re
from .models import Application, Category

class RegisterForm(forms.Form):
    full_name = forms.CharField(label='ФИО', max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
    username = forms.CharField(label='Логин', max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    agree = forms.BooleanField(label='Согласие на обработку персональных данных', widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    def clean_full_name(self):
        v = self.cleaned_data['full_name'].strip()
        if not re.fullmatch(r'[А-Яа-яЁё\s\-]+', v):
            raise forms.ValidationError('ФИО должно содержать только кириллицу, пробелы и дефис.')
        return v

    def clean_username(self):
        v = self.cleaned_data['username']
        if not re.fullmatch(r'[A-Za-z0-9\-]+', v):
            raise forms.ValidationError('Логин должен содержать только латиницу, цифры и дефис.')
        if User.objects.filter(username=v).exists():
            raise forms.ValidationError('Логин уже занят.')
        return v

    def clean(self):
        cleaned = super().clean()
        p = cleaned.get('password')
        p2 = cleaned.get('password2')
        if p and p2 and p != p2:
            self.add_error('password2', 'Пароли не совпадают.')
        return cleaned

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['title', 'description', 'category', 'plan_image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_plan_image(self):
        image = self.cleaned_data.get('plan_image')
        if not image:
            raise ValidationError('Файл обязателен.')
        if image.size > 2 * 1024 * 1024:
            raise ValidationError('Максимальный размер файла 2 Мб.')
        valid_exts = ['jpg','jpeg','png','bmp']
        ext = image.name.split('.')[-1].lower()
        if ext not in valid_exts:
            raise ValidationError('Недопустимый формат файла. Допустимо: jpg, jpeg, png, bmp.')
        return image

class ChangeStatusForm(forms.Form):
    new_status = forms.ChoiceField(choices=[
        ('in_work', 'Принято в работу'),
        ('done', 'Выполнено')
    ])
    admin_comment = forms.CharField(widget=forms.Textarea, required=False)
    design_image = forms.ImageField(required=False)

    def clean(self):
        cleaned = super().clean()
        ns = cleaned.get('new_status')
        if ns == 'in_work' and not cleaned.get('admin_comment'):
            self.add_error('admin_comment', 'Комментарий обязателен при принятии в работу.')
        if ns == 'done' and not cleaned.get('design_image'):
            self.add_error('design_image', 'Изображение дизайна обязательно при завершении.')
        return cleaned

class CategoryForm(forms.ModelForm):
    name = forms.CharField(required=True)
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'})
        }