import os
import pyodbc
from dotenv import load_dotenv

load_dotenv()

SERVER = os.getenv('DB_SERVER')
DATABASE = os.getenv('DB_NAME')
DRIVER = os.getenv('DB_DRIVER')


def get_master_connection():
    conn_str = f'DRIVER={{{DRIVER}}};SERVER={SERVER};Trusted_Connection=yes;'
    return pyodbc.connect(conn_str, autocommit=True)


def get_db_connection():
    conn_str = f'DRIVER={{{DRIVER}}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;'
    return pyodbc.connect(conn_str)


def create_database():
    try:
        conn = get_master_connection()
        cursor = conn.cursor()
        cursor.execute(f"""
            IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = '{DATABASE}')
            CREATE DATABASE {DATABASE}
        """)
        print(f"База данных '{DATABASE}' создана")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Ошибка создания БД: {e}")


def create_table():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Products' AND xtype='U')
            CREATE TABLE Products (
                Id INT IDENTITY(1,1) PRIMARY KEY,
                Название NVARCHAR(100) NOT NULL UNIQUE,
                Тип NVARCHAR(50) NOT NULL,
                Цвет NVARCHAR(50),
                Калорийность INT,
                Описание NVARCHAR(500)
            )
        """)
        conn.commit()
        print("Таблица 'Products' создана")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Ошибка создания таблицы: {e}")


def insert_data():
    products = [
        ('Яблоко', 'Фрукт', 'Красный', 52, 'Сладкое красное яблоко'),
        ('Банан', 'Фрукт', 'Желтый', 89, 'Спелый желтый банан'),
        ('Апельсин', 'Фрукт', 'Оранжевый', 47, 'Сочный цитрусовый фрукт'),
        ('Помидор', 'Овощ', 'Красный', 18, 'Свежий красный помидор'),
        ('Огурец', 'Овощ', 'Зеленый', 15, 'Хрустящий зеленый огурец'),
        ('Морковь', 'Овощ', 'Оранжевый', 41, 'Сладкая оранжевая морковь'),
        ('Виноград', 'Фрукт', 'Фиолетовый', 69, 'Сладкий виноград без косточек'),
        ('Капуста', 'Овощ', 'Белый', 25, 'Белокочанная капуста'),
        ('Груша', 'Фрукт', 'Желтый', 57, 'Сочная желтая груша'),
        ('Брокколи', 'Овощ', 'Зеленый', 34, 'Полезная зеленая брокколи'),
    ]

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        for p in products:
            cursor.execute("""
                IF NOT EXISTS (SELECT 1 FROM Products WHERE Название = ?)
                INSERT INTO Products (Название, Тип, Цвет, Калорийность, Описание)
                VALUES (?, ?, ?, ?, ?)
            """, (p[0], *p))

        conn.commit()
        print(f"Добавлено {len(products)} записей")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Ошибка заполнения: {e}")


def select_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Products")

        columns = [col[0] for col in cursor.description]
        products_list = []

        for row in cursor.fetchall():
            products_list.append(dict(zip(columns, row)))

        print("\nДанные из БД:")
        for p in products_list:
            print(f"{p['Id']}. {p['Название']} - {p['Тип']}, {p['Цвет']}, {p['Калорийность']} ккал")

        cursor.close()
        conn.close()
        return products_list
    except Exception as e:
        print(f"Ошибка выборки: {e}")
        return []


if __name__ == "__main__":
    create_database()
    create_table()
    insert_data()
    select_data()