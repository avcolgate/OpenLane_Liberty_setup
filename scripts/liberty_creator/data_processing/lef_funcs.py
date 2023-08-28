from typing import Any, Tuple
import re

"""
Функция получения значения рамера ячейки из LEF файла

Возвращает кортеж (success, result)
При success = True, result будет содержать размер ячейки                         float
При success = False, result будет содержать сообщение об ошибке                  str
"""
def get_size(file_path: str) -> Tuple[bool, Any]:

    success = True # флаг успешного выполнения функции
    result = ""

    with open(file=file_path, mode='rt') as file:
        lines = file.read().split('\n')
        section_macro = False # флаг секции макроячейки
        macro_name = ''
        area = 0

        for line in lines:
            
            if 'MACRO' in line:
                macro_name = line.replace('MACRO ', '').strip()
                section_macro = True
                continue

            # Получение размера ячейки путем перемножения размеров по X и Y из строки SIZE 
            if section_macro and 'SIZE' in line:
                size = line.replace('SIZE ', '')
                size = re.sub('[;| ]', "", size)
                x, y = size.split('BY')
                area = float(x) * float(y)
                continue

            if section_macro and 'END' in line and macro_name in line:
                section_macro = False
                continue

        # Обработка ошибки, если не найдена макроячейка с указанными именем
        if not macro_name:
            result = "No specified macro found in" + file_path
            success = False

        # Обработка ошибки, если не найден размер у макроячейки с указанными именем
        if not area:
            result = "No size found"
            success = False
        else: 
            result = area

    return success, result
