import psycopg2
from psycopg2 import Error

class Database:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.create_connection()

    def __del__(self):
        if self.connection:
            self.cursor.close()
            self.connection.close()
            print("Соединение с PostgreSQL закрыто")

    def create_connection(self):
        try:
            # Подключение к существующей базе данных
            self.connection = psycopg2.connect(user="aleksandrrybalko",
                                          # пароль, который указали при установке PostgreSQL
                                          password="",
                                          host="127.0.0.1",
                                          port="5432",
                                          database="aleksandrrybalko")

            # Курсор для выполнения операций с базой данных
            self.cursor = self.connection.cursor()
        except (Exception, Error) as error:
            print("Ошибка при работе с PostgreSQL", error)

    def write_contracts(self, contracts):
        self.cursor.execute("""SELECT * FROM contracts""")
        records = self.cursor.fetchall()
        print(records)

        db_contracts = []
        for record in records:
            db_contracts.append(record[1])

        new_contracts = []
        for contract in contracts:
            if contract not in db_contracts:
                new_contracts.append((contract, ))

        sql_insert_query = '''INSERT INTO CONTRACTS(contract_id) VALUES (%S)'''
        self.cursor.executemany(sql_insert_query, new_contracts)
        self.connection.commit()

        return new_contracts
