#!/usr/bin/env python3
# compare_files.py
# Сравнение файлов пользователя и обработанных — только по имени

import os
import json
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class Processed_Files:
    name: str  # полный путь в файле configLLM.json

@dataclass
class ConfigLLM:
    processed_files: List[Processed_Files] = field(default_factory=list)
    prompts: List[dict] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict):
        processed_files = [Processed_Files(**f) for f in data.get("processed_files", [])]
        # Просто сохраняем промты как есть
        return cls(processed_files=processed_files)

    def to_dict(self):
        return {
            "processed_files": [file.__dict__ for file in self.processed_files],
            "prompts": self.prompts
        }


class FileComparator:
    def __init__(self, user_name: str, user_data_dir: str = "user_data"):
        self.user_name = user_name
        self.user_data_dir = user_data_dir
        self.user_folder = os.path.join(self.user_data_dir, self.user_name)
        self.pdf_folder = os.path.join(self.user_folder, "pdf")
        self.config_path = os.path.join(self.user_folder, "configLLM.json")

    def get_all_filenames_in_pdf_folder(self) -> List[str]:
        """Возвращает список имён файлов (только имя) из папки pdf."""
        if not os.path.exists(self.pdf_folder):
            print(f"❌ Папка PDF не найдена: {self.pdf_folder}")
            return []

        valid_extensions = {'.pdf', '.docx', '.pptx'}
        try:
            files = [
                f for f in os.listdir(self.pdf_folder)
                if os.path.isfile(os.path.join(self.pdf_folder, f))
                and os.path.splitext(f.lower())[1] in valid_extensions
            ]
            print(f"✅ Найдено {len(files)} файлов в папке {self.pdf_folder}")
            return files  # только имена: 'doc.pdf', 'file.docx'
        except Exception as e:
            print(f"❌ Ошибка при чтении папки: {e}")
            return []

    def get_processed_filenames_from_config(self) -> List[str]:
        """Читает configLLM.json и возвращает список имён файлов (только имя)."""
        if not os.path.exists(self.config_path):
            print(f"⚠️  Файл configLLM.json не найден: {self.config_path}")
            print("Будет считаться, что обработанных файлов нет.")
            return []

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            config = ConfigLLM.from_dict(data)
            # Извлекаем только имя файла из полного пути
            processed_names = [os.path.basename(file.name) for file in config.processed_files]
            print(f"✅ Загружено {len(processed_names)} записей из configLLM.json")
            return processed_names
        except Exception as e:
            print(f"❌ Ошибка при чтении configLLM.json: {e}")
            return []

    def compare(self) -> dict:
        """Сравнивает файлы по имени и возвращает результат."""
        current_files = set(self.get_all_filenames_in_pdf_folder())
        processed_files = set(self.get_processed_filenames_from_config())

        return {
            "new": sorted(current_files - processed_files),  # есть в папке, но не обработаны
            "already_processed": sorted(current_files & processed_files),  # уже обработаны
            "missing_in_folder": sorted(processed_files - current_files),  # обработаны, но исчезли из папки
        }

    def print_report(self):
        """Выводит понятный отчёт в консоль."""
        print("\n" + "="*60)
        print(f"СРАВНЕНИЕ ФАЙЛОВ: {self.user_name}")
        print("="*60)

        result = self.compare()

        # 1. Новые файлы (требуют обработки)
        print(f"\n🆕 НОВЫЕ ФАЙЛЫ (ещё не обработаны): {len(result['new'])}")
        for name in result['new']:
            print(f"   • {name}")

        # 2. Уже обработанные
        print(f"\n✅ УЖЕ ОБРАБОТАНЫ: {len(result['already_processed'])}")
        for name in result['already_processed']:
            print(f"   • {name}")

        # 3. Пропавшие файлы
        print(f"\n🗑️  ОТСУТСТВУЮТ В ПАПКЕ (но в configLLM): {len(result['missing_in_folder'])}")
        for name in result['missing_in_folder']:
            print(f"   • {name}")

        print("\n" + "="*60)

        # Рекомендации
        if not result['new'] and not result['missing_in_folder']:
            print("📌 Система в актуальном состоянии.")
        elif result['new']:
            print(f"📌 Рекомендуется запустить обработку: найдено {len(result['new'])} новых файлов.")
        else:
            print("📌 Новых файлов нет. Проверьте, нужно ли очистить configLLM от удалённых.")


# =============================
# ЗАПУСК СКРИПТА
# =============================

if __name__ == "__main__":
    # === НАСТРОЙКА ===
    USER_NAME = "ae05d4f9-f962-486f-8166-098106dc8fb1"  # ← замените на нужное имя
    USER_DATA_DIR = "user_data"  # путь к папке user_data

    # Создаём компаратор и запускаем отчёт
    comparator = FileComparator(user_name=USER_NAME, user_data_dir=USER_DATA_DIR)
    comparator.print_report()