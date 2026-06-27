import os
import pyodbc
from dotenv import load_dotenv

load_dotenv()


class DatabaseORM:
    def __init__(self):
        self.server = os.getenv('DB_SERVER')
        self.database = os.getenv('DB_NAME')
        self.driver = os.getenv('DB_DRIVER')

    def _get_master_connection(self):
        conn_str = f'DRIVER={{{self.driver}}};SERVER={self.server};Trusted_Connection=yes;'
        return pyodbc.connect(conn_str, autocommit=True)

    def _get_db_connection(self):
        conn_str = f'DRIVER={{{self.driver}}};SERVER={self.server};DATABASE={self.database};Trusted_Connection=yes;'
        return pyodbc.connect(conn_str, autocommit=True)

    def create_database(self):
        try:
            conn = self._get_master_connection()
            cursor = conn.cursor()
            cursor.execute(f"""
                IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = '{self.database}')
                CREATE DATABASE {self.database}
            """)
            print(f"База данных '{self.database}' создана")
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Ошибка создания БД: {e}")

    def create_table(self):
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Products' AND xtype='U')
                CREATE TABLE Products (
                    Id INT IDENTITY(1,1) PRIMARY KEY,
                    Название NVARCHAR(100) NOT NULL UNIQUE,
                    Тип NVARCHAR(50) NOT NULL,
                    Цвет NVARCHAR(50),
                    Калорийность INT
                )
            """)
            print("Таблица 'Products' создана")
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Ошибка создания таблицы: {e}")

    def drop_table(self):
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                IF EXISTS (SELECT * FROM sysobjects WHERE name='Products' AND xtype='U')
                DROP TABLE Products
            """)
            print("Таблица 'Products' удалена")
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Ошибка удаления таблицы: {e}")

    def drop_database(self):
        try:
            conn = self._get_master_connection()
            cursor = conn.cursor()
            cursor.execute(f"""
                IF EXISTS (SELECT name FROM sys.databases WHERE name = '{self.database}')
                DROP DATABASE {self.database}
            """)
            print(f"База данных '{self.database}' удалена")
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Ошибка удаления БД: {e}")


if __name__ == "__main__":
    db = DatabaseORM()

    print("=== Шаг 1: Создание БД ===")
    db.create_database()

    print("\n=== Шаг 2: Создание таблицы ===")
    db.create_table()

    print("\n=== Шаг 3: Удаление таблицы ===")
    db.drop_table()

    print("\n=== Шаг 4: Удаление БД ===")
    db.drop_database()