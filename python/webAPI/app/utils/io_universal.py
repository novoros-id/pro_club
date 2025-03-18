

def sanitize_filename(name):
    # Список символов, которые необходимо удалить
    invalid_chars = '<>:"/\\|?*'
    
    # Убираем каждый недопустимый символ
    for char in invalid_chars:
        name = name.replace(char, '')
        
    # Также заменяем нуль-символ \0 на пустую строку
    name = name.replace('\0', '')
    
    return name