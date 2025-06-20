
import shutil, datetime
import pandas as pd
import os

required_columns = {'request_text', 'response_text', 'Source'}

class PipelineResult:
    def __init__(self, questions, sources, user_input_folder, steps = None, error = None):
        self.questions = questions
        self.sources = sources
        self.user_input_folder = user_input_folder
        self.steps = steps
        self.error = error

class TestPipelineRunner:
    def __init__(self, zakroma_folder: str, task_folder: str):
        self.zakroma_folder = zakroma_folder
        self.task_folder = task_folder

    def prepare(self, prime_path: str) -> PipelineResult:
        steps = []
            # 1. Чтение файла prime.xls
        try:
            if not os.path.exists(prime_path):
                raise FileNotFoundError(f'Файл prime.xls не найден по пути: {prime_path}')
            
            prime_df = validate_prime_xlsx(prime_path)           
            steps.append('prime.xls прошел все проверки')
        except Exception as e:
            print(f'Ошибка на этапе чтения файла: {e}')
        
            # 2. Подготовка test_user_pipeline и файлов
        try:
            test_username = 'test_user_pipeline'
            user_input_folder = os.path.join(self.task_folder, test_username)
            if not os.path.exists(user_input_folder):
                os.makedirs(user_input_folder)
                steps.append(f'Создана папка пользователя: {user_input_folder}')
            else:
                steps.append(f'Папка пользователя найдена: {user_input_folder}')

            # Подбераем список нужных файлов 
            required_files = list(prime_df['Source'].unique())
            missing_files = []
            copied_files = []

            for fname in required_files:
                fname = str(fname).strip()
                src_path = os.path.join(self.zakroma_folder, fname)
                dst_path = os.path.join(user_input_folder, fname)

                if not os.path.exists(src_path):
                    missing_files.append(fname)
                else:
                    if not os.path.exists(dst_path):
                        shutil.copy(src_path, dst_path)
                        copied_files.append(fname)
            
            if missing_files:
                raise FileNotFoundError(f"В архиве zakroma_folder отсутствуют файлы: {', '.join(missing_files)}")
            
            steps.append(f"Скопированны файлы: {', '.join(copied_files) if copied_files else 'Все были на месте'}")

            # Проверка файлов у пользователя
            user_files = os.listdir(user_input_folder)
            not_copied = [f for f in required_files if f not in user_files]
            if not_copied:
                raise Exception(f"После копирования у пользователя не хватает файлов: {', '.join(not_copied)}")
            
            steps.append(f'Все необходимые файл в папке пользователя {user_input_folder}')

            questions = prime_df['request_text'].tolist()
            sources = prime_df['Source'].tolist()
            return PipelineResult(questions=questions, sources=sources,user_input_folder=user_input_folder, steps=steps)
        
        except Exception as e:
            steps.append(f'Ошибка в class TestPipelineRunner: {e}')

def validate_prime_xlsx(file_path: str) -> pd.DataFrame:
    required_columns = {'request_text', 'response_text', 'Source'}
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        raise ValueError(f"Ошибка при чтении файла prime.xls: {str(e)}")
    columns = set(df.columns)
    missing = required_columns - columns
    if missing:
        raise ValueError(f"В файле отсутствуют необходимые колонки: {', '.join(missing)}")
    nan_counts = df[list(required_columns)].isna().sum()
    if nan_counts.any():
        nan_report = ', '.join([f"{col}: {cnt}" for col, cnt in nan_counts.items() if cnt > 0])
        raise ValueError(f"В обязательных колонках есть пропуски: {nan_report}")
    if len(df) == 0:
        raise ValueError("Файл пустой!")
    if df.duplicated(subset=['request_text', 'Source']).any():
        raise ValueError("Дубликаты по (request_text, Source). Проверь содеражиние prime.xls!")
    return df

def update_prime_file(temp_file_path: str, task_folder: str, zakroma_folder: str) -> str:
    prime_path = os.path.join(task_folder, 'prime.xlsx')
    archive_name = ""
    try:
        # Валидация нового файла перед обновлением
        validate_prime_xlsx(temp_file_path)
        
        # Архивируем старый файл
        if os.path.exists(prime_path):
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            archive_name = f'prime_{timestamp}.xlsx'
            archive_path = os.path.join(zakroma_folder, archive_name)
            shutil.move(prime_path, archive_path)
        # Перемещаем новый файл
        shutil.move(temp_file_path, prime_path)
        return (
            f'Файл prime.xlsx успешно обновлён! '
            + (f"Предыдущий файл был перемещён в архив под именем {archive_name}." if archive_name else "")
        )
    except Exception as e:
        raise RuntimeError(f"Ошибка при обновлении файла prime.xlsx: {str(e)}")

