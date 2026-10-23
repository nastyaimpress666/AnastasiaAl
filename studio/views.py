from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden

from .forms import RegisterForm, ApplicationForm, ChangeStatusForm, CategoryForm
from .models import Application, Category

def home(request):
    last_done = Application.objects.filter(status=Application.STATUS_DONE).order_by('-created_at')[:4]
    in_work_count = Application.objects.filter(status=Application.STATUS_IN_WORK).count()
    return render(request, 'home.html', {'last_done': last_done, 'in_work_count': in_work_count})

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password']
            )
            user.first_name = data['full_name']
            user.save()
            login(request, user)
            return redirect('studio:profile')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('studio:profile')
        else:
            error = 'Неверно логин/пароль'
    return render(request, 'login.html', {'error': error})

def logout_view(request):
    logout(request)
    return redirect('studio:home')

@login_required
def profile(request):
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            app = form.save(commit=False)
            app.author = request.user
            app.save()
            return redirect('studio:profile')
    else:
        form = ApplicationForm()

    status = request.GET.get('status')
    qs = Application.objects.filter(author=request.user).order_by('-created_at')
    if status in [Application.STATUS_NEW, Application.STATUS_IN_WORK, Application.STATUS_DONE]:
        qs = qs.filter(status=status)

    return render(request, 'profile.html', {'applications': qs, 'form': form})

@login_required
def create_application(request):
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            app = form.save(commit=False)
            app.author = request.user
            app.save()
            return redirect('studio:my_applications')
    else:
        form = ApplicationForm()
    return render(request, 'create_application.html', {'form': form})

@login_required
def my_applications(request):
    status = request.GET.get('status')
    qs = Application.objects.filter(author=request.user).order_by('-created_at')
    if status:
        qs = qs.filter(status=status)
    return render(request, 'my_applications.html', {'applications': qs})

@login_required
def delete_application(request, pk):
    app = get_object_or_404(Application, pk=pk)
    if app.author != request.user:
        return HttpResponseForbidden()
    if app.status != Application.STATUS_NEW:
        return HttpResponseForbidden('Нельзя удалить заявку, статус которой изменён администратором')
    if request.method == 'POST':
        app.delete()
        return redirect('studio:my_applications')
    return render(request, 'confirm_delete.html', {'application': app})

def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def admin_app_list(request):
    applications = Application.objects.all().order_by('created_at')
    categories = Category.objects.all()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('studio:admin_app_list')
    else:
        form = CategoryForm()
    return render(request, 'admin_app_list.html', {'applications': applications, "form": form, "categories": categories})

def admin_categories(request):
    categories = Category.objects.all()
    return render(request, "admin/categories.html", { "categories": categories})

@login_required
def delete_category(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    cat.delete()
    return redirect('studio:admin_app_list')

@user_passes_test(is_admin)
def admin_category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('studio:admin_app_list')
    else:
        form = CategoryForm()
    return render(request, "admin/category_create.html", {"form": form})

@user_passes_test(is_admin)
def change_status(request, pk):
    app = get_object_or_404(Application, pk=pk)
    if app.status != Application.STATUS_NEW:
        return HttpResponseForbidden('Смена статуса невозможна (уже работает или выполнено).')
    if request.method == 'POST':
        form = ChangeStatusForm(request.POST, request.FILES)
        if form.is_valid():
            new_status = form.cleaned_data['new_status']
            if new_status == Application.STATUS_IN_WORK:
                app.status = Application.STATUS_IN_WORK
                app.admin_comment = form.cleaned_data['admin_comment']
            elif new_status == Application.STATUS_DONE:
                app.status = Application.STATUS_DONE
                app.design_image = form.cleaned_data['design_image']
            app.save()
            return redirect('studio:admin_app_list')
    else:
        form = ChangeStatusForm()
    return render(request, 'change_status.html', {'form': form, 'application': app})