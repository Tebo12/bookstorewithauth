import sys
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Book
from .forms import RegistrationForm, LoginForm, BookForm
from .utils import login_required, admin_required


def register(request):
    form = RegistrationForm()
    print(request.method)
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password'])  # Хэширование пароля
                user.is_active = True  # Делаем пользователя активным
                user.save()

                print(f"✅ Пользователь {user.username} зарегистрирован.", file=sys.stderr)
                messages.success(request, 'Регистрация успешна! Войдите в аккаунт.')
                return redirect('login')

            except Exception as e:
                print(f"[REGISTER ERROR] {str(e)}", file=sys.stderr)
                messages.error(request, 'Ошибка регистрации. Попробуйте снова.')

        else:
            print(f"[REGISTER ERROR] Некорректная форма: {form.errors}", file=sys.stderr)
            messages.error(request, 'Некорректные данные.')

    return render(request, 'register.html', {'form': form})


def login(request):
    print("login request:", request.method)
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        print(f"🔍 Попытка входа: {username}", file=sys.stderr)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            print(f"✅ Успешная аутентификация пользователя: {user.username}", file=sys.stderr)
            auth_login(request, user)
            return redirect('book_list')
        else:
            print(f"❌ Ошибка входа: Пользователь {username} не найден или неверный пароль", file=sys.stderr)
            messages.error(request, 'Неверное имя пользователя или пароль.')

    return render(request, 'login.html', {'form': LoginForm()})


def logout(request):
    auth_logout(request)  # Используем встроенную функцию Django
    messages.success(request, 'Вы вышли из системы.')
    return redirect('book_list')


def book_list(request):
    books = Book.objects.all()
    return render(request, 'book_list.html', {'books': books})


@login_required
def book_add(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Книга успешно добавлена!')
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'book_add.html', {'form': form})


@admin_required
def book_edit(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Книга успешно обновлена!')
            return redirect('book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'book_edit.html', {'form': form})


@admin_required
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Книга удалена.')
        return redirect('book_list')
    return render(request, 'book_confirm_delete.html', {'book': book})
