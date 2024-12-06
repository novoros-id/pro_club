from io_db import DbHelper

chat_id = '123'
user_name = 'dakinfiev'

db_helper = DbHelper(chat_id, user_name)

db_helper.get_all_user_files()

'''
prompt = "Кому подарили заячий тулупчик?"
answer_text = db_helper.get_answer(prompt)
'''
