from io_db import DbHelper

chat_id = '123'
user_name = 'dakinfiev'

db_helper = DbHelper(chat_id, user_name)

db_helper.processing_user_files()


