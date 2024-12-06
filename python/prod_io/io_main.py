from io_db import DbHelper

chat_id = '123'
user_name = 'dakinfiev'

db_helper = DbHelper(chat_id, user_name)

#db.processing_user_files()


vector_db = db_helper.get_vectror_db()
prompt = "Кому подарили заячий тулупчик?"
answer_text = db_helper.get_answer(vector_db, prompt)

