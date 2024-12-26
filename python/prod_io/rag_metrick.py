import pandas
import io_json
import os

logs_folder_path = io_json.get_config_value('logs_folder_path') 

logs_file_name = os.path.join(logs_folder_path, 'bot_logs.csv')
prime_file_name = os.path.join(logs_folder_path, 'prime.csv')

logs_file = pandas.read_csv(logs_file_name, encoding='utf-8')
prime_file = pandas.read_csv(prime_file_name, encoding='utf-8')