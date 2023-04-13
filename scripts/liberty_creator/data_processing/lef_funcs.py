import os
import re

def get_size(file_path: str) -> float:
    if os.path.splitext(file_path)[1] != '.lef':
        print("fatal (getting module size): extension of input file must be .lef")
        exit()
    if not os.path.exists(file_path):
        print("fatal (getting module size): input file does not exist")
        exit()

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
            print("fatal (getting module size): no macro found in input file")
            exit()
        if not area:
            print("fatal (getting module size): no size found in input file")
            exit()

    return area