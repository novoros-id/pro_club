from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from db_models import Base, User, Program, ConnectionSetting, TypeProgram 

# Настройка подключения к базе данных
DATABASE_URL = "sqlite:///main_api.db"
engine = create_engine(DATABASE_URL, echo=True)

# Создание таблиц
def init_db():
    Base.metadata.create_all(engine)
    print("Таблицы успешно созданы!")

    # Добавление данных
    with Session(engine) as session:
        
        # Создание Пользователей
        users = [
            User(id="dakinfiev", name="dakinfiev", email="dmitrii.akinfiev@1cproconsulting.ru"),
            User(id="dgrishaev", name="dgrishaev", email="dmitriy.grishaev@1cproconsulting.ru"),
            User(id="avaganov", name="avaganov", email="aleksey.vaganov@1cproconsulting.ru"),
        ]
        session.add_all(users)
        session.commit()
        print("Пользователи в базу добавлены!")

        # Создание записей Программ
        programs = [
            Program(program_uid="6a09f20a-8de6-11e1-b3e1-001617ec3f2a", name="1C UH", clienttype=TypeProgram.OneC.value),
            Program(program_uid="e23429d1-c015-4d4b-8ab5-3f0689ef9805", name="Telegram Bot", clienttype=TypeProgram.Telegram.value),
        ]

        #Создание настроек подключения
        connection_settings = [
            ConnectionSetting(program_uid="6a09f20a-8de6-11e1-b3e1-001617ec3f2a",url="http://localhost:8080",client_login="Администратор",client_pass=""),
            ConnectionSetting(program_uid="e23429d1-c015-4d4b-8ab5-3f0689ef9805",url="http://127.0.0.2:8000",client_login="",client_pass="", endpoint="process"),
        ]
       
         # Добавление данных в сессию
        session.add_all(programs)
        session.add_all(connection_settings)

         # Сохранение изменений
        session.commit()
        print("Данные по программам и настройкам программ успешно добавлены!")




if __name__ == "__main__":
    init_db()