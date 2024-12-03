import io_db

chat_id = '123'
user_name = 'dakinfiev'

#io_db.processing_user_files(chat_id, user_name)

vector_db = io_db.get_vectror_db(chat_id, user_name)
prompt = "Кому подарили заячий тулупчик?"
answer_text = io_db.get_answer(chat_id, user_name, vector_db, prompt)