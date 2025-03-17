import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.utils.llm_implementation import io_separate_file as io_separate_file
print("Текущая рабочая директория:", os.getcwd())