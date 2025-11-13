from dotenv import load_dotenv
import psycopg2
import os
from psycopg2 import OperationalError, InterfaceError, DatabaseError

load_dotenv()

class DataBaseManager:
    """
    Класс для управления подключением к базе данных PostgreSQL и выполнения запросов.
    
    Атрибуты:
        connection: Объект подключения к базе данных.
    """
    def __init__(self):
        """
        Инициализирует объект DataBaseManager и устанавливает подключение к базе данных.
        
        Raises:
            Exception: Если не удалось подключиться к базе данных.
        """
        self.connection = None
        try:
            self.connection = self._connect()
        except Exception as e:
            print(f"Ошибка при подключении к БД: {e}")
            raise  # Пробрасываем исключение дальше для обработки на уровне приложения

    def _connect(self):
        """
        Устанавливает подключение к базе данных PostgreSQL.
        
        Returns:
            Объект подключения к базе данных.
            
        Raises:
            OperationalError: Если не удалось подключиться к серверу базы данных.
            Exception: Если произошла неизвестная ошибка при подключении.
        """
        try:
            connect = psycopg2.connect(
                host=os.getenv('HOST_DB'),
                port=os.getenv('PORT_DB'),
                dbname=os.getenv('DB_NAME'),
                user=os.getenv('USER_DB'),
                password=os.getenv('PASSWORD_DB'),
                client_encoding=os.getenv('CLIENT_ENCODING_DB')
            )
            print("Успешное подключение к БД")
            return connect
        except OperationalError as e:
            print(f"Ошибка подключения к серверу БД: {e}")
            raise
        except Exception as e:
            print(f"Неизвестная ошибка при подключении: {e}")
            raise

    def query_database(self, query, params=None, fetch_one=False, reg=False):
        """
        Выполняет SQL-запрос к базе данных.
        
        Args:
            query (str): SQL-запрос.
            params (tuple, optional): Параметры для SQL-запроса. По умолчанию None.
            fetch_one (bool, optional): Если True, возвращает только одну запись. По умолчанию False.
            reg (bool, optional): Если True, не возвращает результат. По умолчанию False.
            
        Returns:
            Результат выполнения запроса или None, если reg=True.
            
        Raises:
            DatabaseError: Если нет подключения к базе данных.
            OperationalError: Если произошла ошибка выполнения запроса.
            InterfaceError: Если произошла ошибка выполнения запроса.
            Exception: Если произошла неизвестная ошибка при выполнении запроса.
        """
        if not self.connection:
            raise DatabaseError("Нет подключения к БД")
            
        cursor = None
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            if not reg:
                result = cursor.fetchone() if fetch_one else cursor.fetchall()
                self.connection.commit()
                return result
                
            self.connection.commit()
            return None
            
        except (OperationalError, InterfaceError) as e:
            print(f"Ошибка выполнения запроса: {e}")
            self.connection.rollback()
            raise
        except Exception as e:
            print(f"Неизвестная ошибка при выполнении запроса: {e}")
            self.connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()

    def close(self):
        """
        Закрывает подключение к базе данных.
        
        Raises:
            Exception: Если произошла ошибка при закрытии соединения.
        """
        try:
            if self.connection and not self.connection.closed:
                self.connection.close()
                print("Соединение с БД закрыто")
        except Exception as e:
            print(f"Ошибка при закрытии соединения: {e}")
            raise

    def __enter__(self):
        """
        Метод для поддержки контекстного менеджера.
        
        Returns:
            Объект DataBaseManager.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Метод для поддержки контекстного менеджера. Закрывает подключение к базе данных.
        
        Args:
            exc_type: Тип исключения.
            exc_val: Значение исключения.
            exc_tb: Объект traceback.
        """
        self.close()

# db = DataBaseManager()

# print(int(db.query_database('select  from users;')[0][0]))