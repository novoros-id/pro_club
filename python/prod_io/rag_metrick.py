import pandas
import io_json
import os
from langchain_ollama import OllamaLLM
from langchain.schema import HumanMessage
import datetime

llm = OllamaLLM(
    model="llama3", temperature = "0.1"
)

class promt_default:
    def __init__(self, logs_folder_path, logs_path_file_name, prime_path_file_name):
        self.logs_folder_path = logs_folder_path
        self.logs_path_file_name = logs_path_file_name
        self.prime_path_file_name = prime_path_file_name
        self.logs_file_name = logs_file_name
    def gmetrics(self):
        logs_folder_path = self.logs_folder_path 
        logs_file_name = self.logs_path_file_name 
        prime_file_name = self.prime_path_file_name
        current_time = datetime.datetime.now()
        m_file_name = f'metrics_{current_time.strftime("%Y-%m-%d_%H-%M-%S")}.csv'
        metrics_file_name = os.path.join(logs_folder_path, m_file_name)

        metrics_file = pandas.DataFrame(columns=['date', 'request_text', 'used_files', 'response_text_log', 'response_text_prime', 'metrics' ])
        metrics_file.to_csv(metrics_file_name, index=False, encoding='utf-8')

        logs_file = pandas.read_csv(logs_file_name, encoding='utf-8')
        prime_file = pandas.read_excel(prime_file_name, header=0)

        for index, row in logs_file.iterrows():
            request_text = row["Question"]
            response_text = row["Answer"]
            used_files = row["Source"]
            filtered_rows = prime_file.query(f"request_text == '{request_text}' & used_files == '{used_files}'")
            if len(filtered_rows) == 0:
                print ("По запросу " + request_text + " не найдено данных")
            else:
                a1 = response_text
                a2 = filtered_rows['Answer'].values

                question = f"Ты учитель и проверяшь информацию от ученика. Тебе предоставлен ответ ученика {a1} и ты должен сравнить его с правильным ответом {a2}. При проверке учитывай точность информации. Если ответы идентинчны, то напиши (Ответ 1). Если ответы различаются, то напиши (Ответ 0) и укажи различия. Ответ дай на русском языке "
                metrix_data = llm.invoke([HumanMessage(content=question)])
                
                date = datetime.datetime.now()

                new_array = pandas.DataFrame([{
                    'date'  : date,
                    'request_text'  : request_text,
                    'used_files'    : used_files,
                    'response_text_log' : a1,
                    'response_text_prime'    : a2,
                    'metrics'        : metrix_data
                }])

                metrics_file = pandas.concat([metrics_file, new_array], ignore_index=True)
                metrics_file.to_csv(metrics_file_name, index=False, encoding='utf-8')

        return metrics_file

