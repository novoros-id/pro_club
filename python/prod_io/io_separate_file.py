# имена классов должны начинаться с sf_
# и отображать основные характеристики (по усмотрению разработчика)

# class sf_default:
#     def __init__(self, file_path):
#         self.file_path = file_path
#     def separate_file(self):
#         import os
#         from langchain_community.document_loaders import PyPDFLoader
#         from langchain_community.document_loaders import Docx2txtLoader
#         from langchain.text_splitter import (
#             RecursiveCharacterTextSplitter,
#         )
#         basename, extension = os.path.splitext(self.file_path)

#         match extension:
#             case ".docx":
#                 loader = Docx2txtLoader(self.file_path)
#             case ".pdf":  
#                 loader = PyPDFLoader(self.file_path)
#             case _:
#                 print(f"Данный файл не поддерживается {self.file_path}")
#                 return []

#         documents = loader.load()

#         text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200,)
#         documents = text_splitter.split_documents(documents)

#         return documents
    
# class sf_500_100_podg:
#     def __init__(self, file_path):
#         self.file_path = file_path
#     def separate_file(self):
#         import os
#         import re 
#         from langchain_community.document_loaders import PyPDFLoader
#         from langchain_community.document_loaders import Docx2txtLoader
#         from langchain.text_splitter import (
#             RecursiveCharacterTextSplitter,
#         )
#         basename, extension = os.path.splitext(self.file_path)

#         match extension:
#             case ".docx":
#                 loader = Docx2txtLoader(self.file_path)
#             case ".pdf":  
#                 loader = PyPDFLoader(self.file_path)
#             case _:
#                 print(f"Данный файл не поддерживается {self.file_path}")
#                 return []

#         documents = loader.load()

#         # pages = []
#         # for doc in documents:
#         #     cleaned_document = doc.replace('\n', '')
#         #     pages.append(cleaned_document)

#         text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100,)
#         documents = text_splitter.split_documents(documents)

#         return documents
# import os
# import fitz
# import pytesseract
# import io
# import camelot
# import matplotlib
# matplotlib.use('Agg') # Используем не интеррактивный режим

# from langchain_community.document_loaders import (
#     Docx2txtLoader, 
#     UnstructuredWordDocumentLoader, 
#     UnstructuredPDFLoader, 
#     PyPDFLoader
# )
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from docx import Document as DocxDocument
# from langchain.docstore.document import Document as LangDocument
# from PIL import Image

# class sfBaseLoader:
#     def __init__(self, file_path, docx_loader: str = "docx2txt", pdf_loader: str = "py", chunk_size: int = 1000, chunk_overlap: int = 200):

#         self.file_path = file_path
#         self.docx_loader = docx_loader
#         self.pdf_loader = pdf_loader
#         self.chunk_size = chunk_size
#         self.chunk_overlap = chunk_overlap

#     # Анализируем содержимое страниц для выбора стратегии обработки    
#     def analyze_page_content(self, page):
#         analysis = {
#             "contains_text": False,
#             "contains_images": False,
#             "contains_tables": False
#         }

#         try:
#             page_dict = page.get_text("dict") #Получаем текстовую разметку страницы
#             for block in page_dict.get("blocks", []):
#                 if "text" in block: #Блок с текстом 
#                     analysis["contains_text"] = True
#                 elif "image" in block: #Блок с изображением 
#                     analysis["contains_images"] = True
#                 elif "lines" in block: #Линии могут указывать на таблицы
#                     analysis["contains_tables"] = True
#         except Exception as e:
#             print(f'Ошибка анализа страницы: {e}')

#         return analysis
    
#     def try_extract_table(self, page_num, page):
#         """
#         Пробует оба режима Camelot ('lattice' и 'stream') для извлечения таблиц
#         и выбирает тот результат, который кажется более качественным.
#         Критерием качества может служить суммарное число строк во всех извлечённых таблицах.
#         """
#         table_text_candidates = {}


#         # flavors = ["lattice", "stream"]
#         page_dict = page.get_text("dict")
#         contains_lines = any("lines" in block for block in page_dict.get("blocks", []))
#         flavors = ["lattice", "stream"] if contains_lines else ["stream"]

#         for flavor in flavors:
#             try:
#                 tables = camelot.read_pdf(self.file_path, pages=str(page_num), flavor=flavor)
#                 if tables.n > 0:
#                     # Рассчитываем простую метрику качества: суммарное число строк во всех таблицах
#                     quality = sum([len(table.df) for table in tables])
#                     table_text = ""
#                     for table in tables:
#                         table_text += table.df.to_csv(index=False) + "\n"
#                     table_text_candidates[flavor] = (quality, table_text)
#                     print(f"Flavor '{flavor}' извлек {tables.n} таблиц на странице {page_num} с метрикой качества {quality}.")
#             except Exception as e:
#                 print(f"Flavor '{flavor}' не сработал на странице {page_num}: {e}")

#         if not table_text_candidates:
#             print(f"❌ На странице {page_num} таблицы не удалось извлечь ни одним из режимов.")
#             return ""

#         # Выбираем режим с максимальной метрикой качества
#         best_flavor = max(table_text_candidates, key=lambda f: table_text_candidates[f][0])
#         best_quality, best_text = table_text_candidates[best_flavor]
#         print(f"✅ Выбран режим '{best_flavor}' для страницы {page_num} с метрикой {best_quality}.")
#         return best_text

#     def extract_content_from_pdf(self):
#         """
#         Извлекает содержимое PDF:
#         - Анализирует каждую страницу (текст, изображения, таблицы).
#         - Извлекает текст с помощью PyMuPDF.
#         - Извлекает изображения и применяет OCR при необходимости.
#         - Извлекает таблицы с помощью Camelot (автоматически выбирая лучший режим).
#         """
#         extracted_texts = []

#         try:
#             doc = fitz.open(self.file_path)
#         except Exception as e:
#             print(f'Ошибка открытия PDF файла {self.file_path}: {e}')
#             return None

#         for page in doc:
#             page_num = page.number + 1  # Нумерация страниц начинается с 1
#             page_analysis = self.analyze_page_content(page) # Анализируем содержимое страниц

#             text = ""
#             table_text = ""

#             # Извлечение текста (если он есть)
#             if page_analysis["contains_text"]:
#                 try:
#                     text = page.get_text("text").strip()
#                 except Exception as e:
#                     print(f'Ошибка измлечения текста на странице {page_num}: {e}')
            
#             # Если текста нет, но есть изображения, применяем OCR
#             if not text and page_analysis["contains_images"]:
#                 try:
#                     pix = page.get_pixmap()
#                     image = Image.open(io.BytesIO(pix.tobytes()))
#                     text = pytesseract.image_to_string(image).strip()
#                 except Exception as e:
#                     print(f'Ошибка при выполении OCR на странице {page_num}: {e}')
            
#             # Если обнаружены таблицы, запускаем Camelot с правильным режимом
#             if page_analysis["contains_tables"]:
#                 table_text = self.try_extract_table(page_num, page)
            
#             # Объединяем текст и таблицы
#             combined = ""

#             if text:
#                 combined += "Текст:\n" + text
#             if table_text:
#                 if combined:
#                     combined += "\n\n"
#                 combined += "Таблицы:\n" + table_text
#             if combined:
#                 extracted_texts.append(combined)

#         return "\n\n".join(extracted_texts) if extracted_texts else None

#     def separate_file(self):
#         _, extension = os.path.splitext(self.file_path)
#         extension = extension.lower()
#         table_text = None
#         documents = []

#         #Выбор загрузчика на основе расширения файла
#         if extension == ".docx":
#             if self.docx_loader == "unstructured":
#                 loader = UnstructuredWordDocumentLoader(self.file_path)
#             else:
#                 loader = Docx2txtLoader(self.file_path)
#             table_text = self.extract_tables_from_docx()

#         elif extension == ".pdf":
#             if self.pdf_loader == "py":
#                 loader = PyPDFLoader(self.file_path)
#             else:
#                 loader = UnstructuredPDFLoader(self.file_path)
#             table_text = self.extract_content_from_pdf()
#         else:
#             print(f"Расширение файла не поддерживается {self.file_path}")
#             return []
        
#         #Загрузка основного текста документа
#         try:
#             documents = loader.load()
#         except Exception as e:
#             print(f'Ошибка загрузки основного текста документа {e}')
#             documents = []

#         # Если извлечены таблицы, добавляем их как дополнительный документа
#         if table_text is not None and table_text.strip():
#             documents.append(LangDocument(page_content=table_text))

#         # Разделение текста на чанки
#         try:
#             text_splitter = RecursiveCharacterTextSplitter(
#                 chunk_size=self.chunk_size,
#                 chunk_overlap=self.chunk_overlap
#             )
#             documents = text_splitter.split_documents(documents)
#         except Exception as e:
#             print(f'Ошибка разделения документа на чанки {e}')
#         return documents

# class sfDefault(sfBaseLoader):
#     def __init__(self, file_path: str, docx_loader: str = "docx2txt", pdf_loader: str = "py"):
#         super().__init__(file_path, docx_loader, pdf_loader, chunk_size=1000, chunk_overlap=200)

# class sf500100Podg(sfBaseLoader):
#     def __init__(self, file_path: str, docx_loader: str = "docx2txt", pdf_loader: str = "py"):
#         super().__init__(file_path, docx_loader, pdf_loader, chunk_size=500, chunk_overlap=100)

# class sfDefaultUND(sfBaseLoader):
#     def __init__(self, file_path: str, docx_loader: str = "unstructured_docx", pdf_loader: str = "unstructured_pdf"):
#         super().__init__(file_path, docx_loader, pdf_loader, chunk_size=1000, chunk_overlap=200)

# class sf500100PodgUND(sfBaseLoader):
#     def __init__(self, file_path: str, docx_loader: str = "unstructured_docx", pdf_loader: str = "unstructured_pdf"):
#         super().__init__(file_path, docx_loader, pdf_loader, chunk_size=500, chunk_overlap=100)


import os
import io

# Класс для определения расширения файла
class sfFileTypeDetector:
    @staticmethod
    def get_file_type(file_path: str) -> str:
        _, ext = os.path.splitext(file_path)
        return ext.lower()

# Класс для загрузки DOCX
# class sfDocxLoader:
#     def __init__(self, file_path: str, loader_type: str = "docx2txt"):
#         self.file_path = file_path
#         self.loader_type = loader_type

#     def load_documents(self):
#         # Выбор стратегии загрузки для DOCX
#         if self.loader_type == "docx2txt":
#             from langchain_community.document_loaders import Docx2txtLoader
#             loader = Docx2txtLoader(self.file_path)
#         elif self.loader_type == "unstructured":
#             from langchain_community.document_loaders import UnstructuredWordDocumentLoader
#             loader = UnstructuredWordDocumentLoader(self.file_path)
#         else:
#             raise ValueError(f"Неизвестный тип загрузчика для DOCX: {self.loader_type}")
        
#         documents = loader.load()
#         # Извлечение таблиц (заглушка, до доработки)
#         table_text = self.extract_tables_from_docx()
#         if table_text and table_text.strip():
#             from langchain.docstore.document import Document as LangDocument
#             documents.append(LangDocument(page_content=table_text))
#         return documents

#     def extract_tables_from_docx(self):
#         print("Метод extract_tables_from_docx не реализован.")
#         return ""

# Класс для извлеченя текста из DOCX, включая списки, заголовки и обычные абзацы
class sfDOCXTextExtractor:
    def __init__(self, file_path: str):
        self.file_path = file_path
    
    def extract_text(self) -> str:
        from docx import Document as DocxDocument
        try:
            doc = DocxDocument(self.file_path)
            text_data = []
            for para in doc.paragraphs:
                if para.style.name.startswith("Heading"): # Сохранение загаловков
                    text_data.append(f"\n**{para.text.strip()}**")
                else:
                    text_data.append(para.text.strip())
            return "\n".join(text_data)
        except Exception as e:
            print(f"Ошибка извлечения текста: {e}")
            return ""

# Класс для извлечения таблиц из DOCX
class sfDOCXTableExtractor:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def extract_tables(self) -> str:
        from docx import Document as DocxDocument
        try:
            doc = DocxDocument(self.file_path)
            tables_text = []
            for table in doc.tables:
                rows = []
                for row in table.rows:
                    cells = [cell.text.strip() for cell in row.cells]
                    rows.append("\t".join(cells))
                tables_text.append("\n".join(rows))
            return "\n\n".join(tables_text)
        except Exception as e:
            print(f"Ошибка извлечения таблиц: {e}")
            return ""

# Класс для извлечения изображений из DOCX и применения OCR        
class sfDOCXImageExtractor:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def extract_images_text(self) -> str:
        import zipfile
        import pytesseract
        from PIL import Image

        ocr_text = []
        try:
            with zipfile.ZipFile(self.file_path) as docx_zip:
                for file in docx_zip.namelist():
                    if file.startswith("word/media/"):
                        try:
                            image_data = docx_zip.read(file)
                            image = Image.open(io.BytesIO(image_data))
                            text = pytesseract.image_to_string(image).strip()
                            if text:
                                ocr_text.append(text)
                        except Exception as img_e:
                            print(f"Ошибка обработки изображения {file}: {img_e}")
        except Exception as e:
            print (f"Ошибка открытия DOCX как zip-архива: {e}")
        return "\n\n".join(ocr_text)
            
# Фабрика для обработки DOCX (извлечение текста, таблиц, изображения
class sfDOCXLoader:
    def __init__(self, file_path: str, loader_type: str = "python-docx"):
        self.file_path = file_path
        self.loader_type = loader_type
        self.text_extractor = sfDOCXTextExtractor(file_path)
        self.table_extractor = sfDOCXTableExtractor(file_path)
        self.image_extractor = sfDOCXImageExtractor(file_path)

    def load_documents(self):
        from langchain.docstore.document import Document as LangDocument
        documents = []

        # Извлечение текста
        text = self.text_extractor.extract_text()
        if text.strip():
            documents.append(LangDocument(page_content=text))

        # Извлечение таблиц
        table_text = self.table_extractor.extract_tables()
        if table_text.strip():
            documents.append(LangDocument(page_content=table_text))

        # Извлечение текста из изображений
        images_text = self.image_extractor.extract_images_text()
        if images_text.strip():
            documents.append(LangDocument(page_content=images_text))

        return documents

#  Класс для извлечения текста и анализа страницы PDF
class sfPDFTextExtractor:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def analyze_page(self, page):
        analysis = {"contains_text": False, "contains_images": False, "contains_tables": False}
        try:
            page_dict = page.get_text("dict")
            for block in page_dict.get("blocks", []):
                if "text" in block and block["text"].strip():
                    analysis["contains_text"] = True
                if "image" in block:
                    analysis["contains_images"] = True
                if "lines" in block:
                    analysis["contains_tables"] = True
        except Exception as e:
            print(f"Ошибка анализа страницы: {e}")
        return analysis

    def extract_text(self, page):
        text = ""
        analysis = self.analyze_page(page)
        if analysis["contains_text"]:
            try:
                text = page.get_text("text").strip()
            except Exception as e:
                print(f"Ошибка извлечения текста: {e}")
        elif analysis["contains_images"]:
            try:
                pix = page.get_pixmap()
                from PIL import Image
                image = Image.open(io.BytesIO(pix.tobytes()))
                import pytesseract
                text = pytesseract.image_to_string(image).strip()
            except Exception as e:
                print(f"Ошибка OCR: {e}")
        return text

# Класс для извлечения таблиц из PDF
class sfPDFTableExtractor:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def try_extract_table(self, page_num, page):
        import camelot
        table_text_candidates = {}

        try:
            page_dict = page.get_text("dict")
            contains_lines = any("lines" in block for block in page_dict.get("blocks", []))
            flavors = ["lattice", "stream"] if contains_lines else ["stream"]
            
            for flavor in flavors:
                try:
                    tables = camelot.read_pdf(self.file_path, pages=str(page_num), flavor=flavor)
                    if tables.n > 0:
                        quality = sum(len(table.df) for table in tables)
                        table_text = "\n".join([table.df.to_csv(index=False) for table in tables])
                        table_text_candidates[flavor] = (quality, table_text)
                        print(f"Flavor '{flavor}' извлек {tables.n} таблиц на странице {page_num} с качеством {quality}.")
                except Exception as e:
                    print(f"Flavor '{flavor}' не сработал на странице {page_num}: {e}")

            if not table_text_candidates:
                print(f"Таблицы не извлечены на странице {page_num}.")
                return ""
                        
            best_flavor = max(table_text_candidates, key=lambda f: table_text_candidates[f][0])
            best_quality, best_text = table_text_candidates[best_flavor]
            print(f"Выбран режим '{best_flavor}' для страницы {page_num} с качеством {best_quality}.")
            return best_text
        except Exception as e:
            print(f"Ошибка извлечения таблиц: {e}")
            return ""

    def extract_tables(self):
        extracted_tables = []
        import fitz  # PyMuPDF

        try:
            doc = fitz.open(self.file_path)
        except Exception as e:
            print(f"Ошибка открытия PDF: {e}")
            return ""
        
        for page in doc:
            page_num = page.number + 1
            analysis = sfPDFTextExtractor(self.file_path).analyze_page(page)
            if analysis["contains_tables"]:
                table_text = self.try_extract_table(page_num, page)
                if table_text:
                    extracted_tables.append(table_text)
        return "\n\n".join(extracted_tables) if extracted_tables else ""

# Класс для загрузки PDF, объединяющий текст и таблицы
class sfPDFLoader:
    def __init__(self, file_path: str, loader_type: str = "unstructured"):
        self.file_path = file_path
        self.loader_type = loader_type
        self.text_extractor = sfPDFTextExtractor(file_path)
        self.table_extractor = sfPDFTableExtractor(file_path)

    def load_documents(self):
        if self.loader_type == "py":
            from langchain_community.document_loaders import PyPDFLoader
            loader = PyPDFLoader(self.file_path)
        elif self.loader_type == "unstructured":
            from langchain_community.document_loaders import UnstructuredPDFLoader
            loader = UnstructuredPDFLoader(self.file_path)
        else:
            raise ValueError(f"Неизвестный тип загрузчика для PDF: {self.loader_type}")
        
        documents = loader.load()
        # Извлечение таблиц
        tables_text = self.table_extractor.extract_tables()
        if tables_text.strip():
            from langchain.docstore.document import Document as LangDocument
            documents.append(LangDocument(page_content=tables_text))
        return documents

# Класс для разделения текста на чанки
class sfTextSplitter:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        self.splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    
    def split(self, documents):
        return self.splitter.split_documents(documents)

# Фабрика загрузчиков, которая определяет тип файла и возвращает нужный загрузчик
class sfDocumentLoaderFactory:
    @staticmethod
    def create_loader(file_path: str, **kwargs):
        ext = sfFileTypeDetector.get_file_type(file_path)
        if ext == ".pdf":
            loader_type = kwargs.get("pdf_loader", "unstructured")
            return sfPDFLoader(file_path, loader_type=loader_type)
        elif ext == ".docx":
            # loader_type = kwargs.get("docx_loader", "docx2txt")
            loader_type = kwargs.get("python-docx")
            return sfDOCXLoader(file_path, loader_type=loader_type)
        else:
            raise ValueError(f"Неподдерживаемый формат файла: {ext}")

#  Конвейер обработки документа: загрузка -> разделение на чанки
class sfDocumentProcessingPipeline:
    def __init__(self, file_path: str, chunk_size: int = 1000, chunk_overlap: int = 200, **loader_kwargs):
        self.loader = sfDocumentLoaderFactory.create_loader(file_path, **loader_kwargs)
        self.splitter = sfTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    
    def separate_file(self):
        documents = self.loader.load_documents()
        return self.splitter.split(documents)