from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import RegisterForm
from .models import Expense, Category
from django.contrib.auth.views import LogoutView
from decimal import Decimal
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from decimal import Decimal, InvalidOperation

def home(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return redirect('dashboard')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']  # Используем email из формы
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)  # Аутентификация по email
        if user is not None:
            login(request, user)
            messages.success(request, 'Вы успешно вошли в аккаунт!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')
    return render(request, 'app/login.html')

@login_required
def dashboard(request):
    # Последние 6 траты
    recent_expenses = Expense.objects.filter(
        user=request.user
    ).select_related('category').order_by('-date')[:6]

    # Все категории пользователя
    user_categories = Category.objects.filter(user=request.user)

    context = {
        'recent_expenses': recent_expenses,
        'user_categories': user_categories,
    }
    return render(request, 'app/dashboard.html', context)

@login_required
def expenses(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.GET.get('action') == 'get_expense':
        try:
            expense = Expense.objects.get(id=request.GET['id'], user=request.user)
            return JsonResponse({
                'success': True,
                'expense': {
                    'id': expense.id,
                    'amount': str(expense.amount),
                    'category_id': expense.category.id,
                    'description': expense.description or '',
                    'date': expense.date.isoformat()
                }
            })
        except Expense.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Не найдено'}, status=404)

    # === POST: Редактирование ===
    if request.method == 'POST' and request.POST.get('action') == 'edit_expense':
        try:
            expense = Expense.objects.get(id=request.POST['expense_id'], user=request.user)
            amount = Decimal(request.POST['amount'])
            if amount <= 0: raise ValueError('Сумма должна быть > 0')
            category = Category.objects.get(id=request.POST['category'], user=request.user)

            expense.amount = amount
            expense.category = category
            expense.description = request.POST.get('description', '').strip()
            expense.date = request.POST['date']
            expense.save()

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    # === POST: Удаление ===
    if request.method == 'POST' and request.POST.get('action') == 'delete_expense':
        try:
            expense = Expense.objects.get(id=request.POST['expense_id'], user=request.user)
            expense.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    # === POST: Создание категории (AJAX) ===
    if request.method == 'POST' and request.POST.get('action') == 'create_category':
        name = request.POST.get('name', '').strip()
        if not name:
            return JsonResponse({'success': False, 'error': 'Название обязательно'}, status=400)
        if Category.objects.filter(name=name, user=request.user).exists():
            return JsonResponse({'success': False, 'error': 'Такая категория уже существует'}, status=400)

        category = Category.objects.create(user=request.user, name=name)
        return JsonResponse({
            'success': True,
            'category': {
                'id': category.id,      # ← ОБЯЗАТЕЛЬНО!
                'name': category.name
            }
        })

    # === POST: Добавление новой траты ===
    if request.method == 'POST' and request.POST.get('action') == 'add_expense':
        # Проверяем, AJAX-запрос ли это
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        try:
            amount_str = request.POST.get('amount', '').strip()
            if not amount_str:
                raise ValueError('Сумма обязательна')
            try:
                amount = Decimal(amount_str)
                if amount <= 0:
                    raise ValueError('Сумма должна быть больше 0')
            except InvalidOperation:
                raise ValueError('Введите корректную сумму (например: 123.45)')

            category_id = request.POST.get('category')
            if not category_id:
                raise ValueError('Выберите категорию')
            category = Category.objects.get(id=category_id, user=request.user)

            date_str = request.POST.get('date')
            if not date_str:
                raise ValueError('Дата обязательна')

            description = request.POST.get('description', '').strip()

            Expense.objects.create(
                user=request.user,
                category=category,
                amount=amount,
                description=description,
                date=date_str
            )

            if is_ajax:
                return JsonResponse({'success': True})
            else:
                messages.success(request, 'Трата успешно добавлена!')
                return redirect('expenses')

        except Category.DoesNotExist:
            error_msg = 'Выбранная категория не существует.'
        except ValueError as e:
            error_msg = str(e)
        except Exception as e:
            error_msg = 'Неизвестная ошибка.'
            print(e)

        if is_ajax:
            return JsonResponse({'success': False, 'error': error_msg}, status=400)
        else:
            messages.error(request, error_msg)
            return redirect('expenses')

    # === GET ===
    expenses = Expense.objects.filter(user=request.user)\
        .select_related('category')\
        .order_by('-date', '-id')  # Сначала по дате, потом по ID
    categories = Category.objects.filter(user=request.user)
    today = timezone.now().date()

    context = {
        'expenses': expenses,
        'categories': categories,
        'today': today,
    }
    return render(request, 'app/expenses.html', context)

@login_required
def reports(request):
    context = {
        'page_title': 'Отчёты',
        'monthly_data': [100, 200, 300, 1200, 800, 900],  # Январь — Июнь
        'pie_data': [
            {'category': 'Еда', 'amount': 450},
            {'category': 'Квартплата', 'amount': 1200},
            {'category': 'Комуслуги', 'amount': 150},
            {'category': 'Транспорт', 'amount': 300},
        ]
    }
    return render(request, 'app/reports.html', context)


@login_required
def categories(request):
    context = {
        'page_title': 'Категории',
        'categories': [
            {'name': 'Еда', 'icon': 'utensils'},
            {'name': 'Квартплата', 'icon': 'home'},
            {'name': 'Комуслуги', 'icon': 'zap'},
            {'name': 'Транспорт', 'icon': 'car'},
            {'name': 'Развлечения', 'icon': 'gamepad-2'},
        ]
    }
    return render(request, 'app/categories.html', context)


@login_required
def settings(request):
    context = {
        'page_title': 'Настройки',
        'user': request.user,
    }
    return render(request, 'app/settings.html', context)

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Регистрация прошла успешно! Теперь вы можете войти.')
            return redirect('login')
        else:
            messages.error(request, 'Ошибка при регистрации. Проверьте введённые данные.')
    else:
        form = RegisterForm()
    return render(request, 'app/register.html', {'form': form})

class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST':
            messages.success(request, 'Вы успешно вышли из аккаунта.')
        return super().dispatch(request, *args, **kwargs)