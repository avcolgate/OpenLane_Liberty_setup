from typing import Any, Tuple
import os
import re

def get_size(file_path: str) -> Tuple[bool, Any]:
    """
    Возвращает кортеж (success, result)
    При success = True, result будет содержать размер ячейки                         float
    При success = False, result будет содержать сообщение об ошибке                  str
    """
    success = True
    result = ""

    file_name, file_extension = os.path.splitext(file_path)

    with open(file=file_path, mode='rt') as file:
        lines = file.read().split('\n')
        section_macro = False
        macro_name = ''
        area = 0

        for line in lines:
            # print(line)
            if 'MACRO' in line:
                macro_name = line.replace('MACRO ', '').strip()
                section_macro = True
                continue

            if section_macro and 'SIZE' in line:
                size = line.replace('SIZE ', '')
                size = re.sub("[;| ]", "", size)
                x, y = size.split('BY')
                area = float(x) * float(y)
                continue

            if section_macro and 'END' in line and macro_name in line:
                section_macro = False
                continue

        if not macro_name:
            result = "No specified macro found in" + file_path
            success = False
        if not area:
            result = "No size found"
            success = False
        else: 
            result = area

    return (success, result)