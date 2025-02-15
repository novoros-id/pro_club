import os
import io
from abc import ABC, abstractmethod
from langchain.docstore.document import Document as LangDocument

# Абстрактный базовый класс для загрузчиков документов
class sfBaseDocumentLoader(ABC):
    @abstractmethod
    def load_documents(self) -> list:
        # Метод должен вернуть список объектов LangDocument
        pass

# Класс для определения расширения файла
class sfFileTypeDetector:
    @staticmethod
    def get_file_type(file_path: str) -> str:
        _, ext = os.path.splitext(file_path)
        return ext.lower()


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
class sfDOCXLoader(sfBaseDocumentLoader):
    def __init__(self, file_path: str, loader_type: str = "python-docx"):
        self.file_path = file_path
        self.loader_type = loader_type
        self.text_extractor = sfDOCXTextExtractor(file_path)
        self.table_extractor = sfDOCXTableExtractor(file_path)
        self.image_extractor = sfDOCXImageExtractor(file_path)

    def load_documents(self):
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
    def __init__(self, file_path: str, text_extractor: sfPDFTextExtractor = None):
        self.file_path = file_path
        self.text_extrarctor = text_extractor if text_extractor is not None else sfPDFTextExtractor(path)
        self._cache = {} # Словарь для кэширования результатов

    def try_extract_table(self, page_num, page):
        # Проверим есть ли результат в кэше
        if page_num in self._cache:
            return self._cache[page_num]

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
                self._cache[page_num] = ""
                return ""
                        
            best_flavor = max(table_text_candidates, key=lambda f: table_text_candidates[f][0])
            best_quality, best_text = table_text_candidates[best_flavor]
            print(f"Выбран режим '{best_flavor}' для страницы {page_num} с качеством {best_quality}.")
            self._cache[page_num] = best_text
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
class sfPDFLoader(sfBaseDocumentLoader):
    def __init__(self, file_path: str, loader_type: str = "unstructured"):
        self.file_path = file_path
        self.loader_type = loader_type
        self.text_extractor = sfPDFTextExtractor(file_path)
        self.table_extractor = sfPDFTableExtractor(file_path, text_extractor=self.text_extractor)

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
            documents.append(LangDocument(page_content=tables_text))
        return documents

# Класс для разделения текста на чанки
class sfTextSplitter:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 200):
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
    def __init__(self, file_path: str, chunk_size: int = 500, chunk_overlap: int = 200, **loader_kwargs):
        self.loader = sfDocumentLoaderFactory.create_loader(file_path, **loader_kwargs)
        self.splitter = sfTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    
    def separate_file(self):
        documents = self.loader.load_documents()
        return self.splitter.split(documents)