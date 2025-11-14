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

def create_volunteer_request(request):
    # Проверяем, что пользователь авторизован и имеет роль "Нуждающийся"
    if 'username' not in request.session:
        return render(request, 'main/logIn.html', {'message': 'Для подачи заявки необходимо авторизоваться'})
    
    if request.session.get('role') != 'Нуждающийся':
        return render(request, 'main/main.html', {'message': 'Только нуждающиеся могут подавать заявки на волонтерскую помощь'})
    
    if request.method == 'POST':
        # Получаем данные из формы
        address = request.POST.get('address')
        time = request.POST.get('time')
        work_type = request.POST.get('work_type')
        hours = request.POST.get('hours')
        
        # Получаем ID пользователя из базы данных
        db_result = db.query_database('SELECT id FROM users WHERE login = %s', params=[request.session['username']])
        if not db_result:
            return render(request, 'main/main.html', {'message': 'Ошибка: пользователь не найден'})
        
        user_id = db_result[0][0]
        
        # Сохраняем заявку в базу данных
        try:
            db.query_database(
                'INSERT INTO volunteer_requests (user_id, address, time, work_type, hours) VALUES (%s, %s, %s, %s, %s)',
                params=[user_id, address, time, work_type, hours],
                reg=True
            )
            return render(request, 'main/main.html', {'message': 'Заявка успешно подана'})
        except Exception as e:
            return render(request, 'main/create_volunteer_request.html', {'message': f'Ошибка при подаче заявки: {str(e)}'})
    
    # Если метод GET, отображаем форму
    return render(request, 'main/create_volunteer_request.html')

def view_volunteer_requests(request):
    # Проверяем, что пользователь авторизован и имеет роль "Волонтёр"
    if 'username' not in request.session:
        return render(request, 'main/logIn.html', {'message': 'Для просмотра заявок необходимо авторизоваться'})
    
    if request.session.get('role') != 'Волонтёр':
        return render(request, 'main/main.html', {'message': 'Только волонтеры могут просматривать заявки'})
    
    # Получаем активные заявки из базы данных
    try:
        db_result = db.query_database('''
            SELECT vr.id, u.login, vr.address, vr.time, vr.work_type, vr.hours
            FROM volunteer_requests vr
            JOIN users u ON vr.user_id = u.id
            WHERE vr.status = 'active'
        ''')
        
        # Преобразуем результат в список словарей для удобства отображения
        requests = []
        for row in db_result:
            requests.append({
                'id': row[0],
                'user': row[1],
                'address': row[2],
                'time': row[3],
                'work_type': row[4],
                'hours': row[5]
            })
        
        return render(request, 'main/view_volunteer_requests.html', {'requests': requests})
    except Exception as e:
        return render(request, 'main/main.html', {'message': f'Ошибка при получении заявок: {str(e)}'})

def accept_volunteer_request(request):
    # Проверяем, что пользователь авторизован и имеет роль "Волонтёр"
    if 'username' not in request.session:
        return render(request, 'main/logIn.html', {'message': 'Для принятия заявки необходимо авторизоваться'})
    
    if request.session.get('role') != 'Волонтёр':
        return render(request, 'main/main.html', {'message': 'Только волонтеры могут принимать заявки'})
    
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        
        # Проверяем, что заявка существует и активна
        db_result = db.query_database(
            'SELECT id FROM volunteer_requests WHERE id = %s AND status = %s',
            params=[request_id, 'active']
        )
        
        if not db_result:
            return render(request, 'main/main.html', {'message': 'Заявка не найдена или уже принята'})
        
        # Обновляем статус заявки на "принята"
        try:
            db.query_database(
                'UPDATE volunteer_requests SET status = %s WHERE id = %s',
                params=['accepted', request_id],
                reg=True
            )
            return render(request, 'main/main.html', {'message': 'Заявка успешно принята'})
        except Exception as e:
            return render(request, 'main/main.html', {'message': f'Ошибка при принятии заявки: {str(e)}'})
    
    # Если метод GET, перенаправляем на страницу просмотра заявок
    return render(request, 'main/view_volunteer_requests.html')