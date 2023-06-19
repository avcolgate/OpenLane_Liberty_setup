from typing import Any, Tuple


def get_leakage(file_path: str) -> Tuple[bool, Any]:
    """
    Возвращает кортеж (success, result)
    При success = True, result будет содержать значение утечки мощности     float
    При success = False, result будет содержать сообщение об ошибке         str
    """
    success = True
    result = ""

    group_list = list()
    total_list = list()
    leakage_num = -1
    leakage = -1

    with open(file=file_path, mode='rt') as file:
        lines = file.read().split('\n')

        for line in lines:
            if 'Group' in line and \
                    'Leakage' in line and not group_list:
                group_list = line.split()
                for num, item in enumerate(group_list):
                    if str(item) == 'Leakage':
                        leakage_num = num
                continue

            if 'Total' in line and group_list:
                total_list = line.split()
                leakage = float(total_list[leakage_num])
                break

        if not group_list:
            result = "Group line not found in OpenSTA log " + file_path
            success = False
        if not total_list:
            result = "Total line not found in OpenSTA log " + file_path
            success = False

    if leakage == -1:
        result = "Leakage not found in OpenSTA log " + file_path
        success = False
    else:
        result = leakage

    return success, result
