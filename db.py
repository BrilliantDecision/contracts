import psycopg2
from psycopg2 import Error


def create_connection(articles_list: list):
    connection = None
    cursor = None

    try:
        # Подключение к существующей базе данных
        connection = psycopg2.connect(user="postgres",
                                      # пароль, который указали при установке PostgreSQL
                                      password="alexandr999",
                                      host="127.0.0.1",
                                      port="5432",
                                      database="postgres")

        # Курсор для выполнения операций с базой данных
        cursor = connection.cursor()

        cursor.execute("INSERT INTO ARTICLE (article_id) VALUES (%s)", ['127897897893456', ])

        connection.commit()
        cursor.execute("SELECT * from ARTICLE")
        print("Результат", cursor.fetchall())
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Соединение с PostgreSQL закрыто")


create_connection([])
