import hashlib
from django.shortcuts import render
from django.http import HttpResponse
from managers.dataBase import DataBaseManager


db = DataBaseManager()

# Create your views here.


def check_login(login):
    db_result = db.query_database('select 1 from users where login = %s', params=[login])

    if db_result and db_result[0][0]:
        return True
    return False

def main(request):
    return render(request, 'main/main.html')


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')

        if check_login(username):
            return render(request, 'main/register.html', {'message': 'Пользователь с таким логином уже существует'})

        hash_password = hashlib.sha256(password.encode()).hexdigest()

        db.query_database('insert into users (login, pwd, role) values (%s, %s, %s)', params=[username, hash_password, role], reg=True)
        
        return render(request, 'main/register.html', {'message': 'Регистрация пройдена, можете перейти на авторизацию'} )
        
    return render(request, 'main/register.html')



def logIn(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Хешируем пароль для сравнения с базой данных
        hash_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Проверяем учетные данные пользователя
        db_result = db.query_database(
            'SELECT 1 FROM users WHERE login = %s AND pwd = %s',
            params=[username, hash_password]
        )
        
        if db_result and db_result[0][0]:
            # Успешная авторизация
            # Устанавливаем сессию для пользователя
            request.session['username'] = username
            request.session['role'] = db.query_database(
                'SELECT role FROM users WHERE login = %s',
                params=[username]
            )[0][0]
           
            # Перенаправляем на главную страницу
            return render(request, 'main/main.html', {'message': 'Вы успешно вошли в систему'})
        else:
            # Неверные учетные данные
            return render(request, 'main/logIn.html', {'message': 'Неверный логин или пароль'})
    
    # Если метод GET, отображаем форму входа
    return render(request, 'main/logIn.html')

def logout(request):
    # Удаляем сессию пользователя
    if 'username' in request.session:
        del request.session['username']
    return render(request, 'main/main.html', {'message': 'Вы успешно вышли из системы'})
    return render(request, 'main/logIn.html')