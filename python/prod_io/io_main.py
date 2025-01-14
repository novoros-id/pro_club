from io_db import DbHelper
import rag_metrick

#chat_id = '123'
#user_name = 'dakinfiev'

#db_helper = DbHelper(chat_id, user_name)

#db_helper.processing_user_files()

task_for_test_folder = "/Users/alexeyvaganov/doc/files/folder_io_project/task_for_test"
log_file_name = "/Users/alexeyvaganov/doc/files/folder_io_project/test_pipline_2025-01-13_22-57-49.csv"
prime_file_path = "/Users/alexeyvaganov/doc/files/folder_io_project/task_for_test/prime.xlsx"

metrick = rag_metrick.rag_metrick(task_for_test_folder, log_file_name, prime_file_path)
file_metrick = metrick.gmetrics()
print (file_metrick)

