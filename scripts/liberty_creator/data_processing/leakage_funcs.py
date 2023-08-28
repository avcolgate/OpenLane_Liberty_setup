from typing import Any, Tuple

"""
Функция получения значения утечки мощности

Возвращает кортеж (success, result)
При success = True,  result будет содержать значение утечки мощности     float
При success = False, result будет содержать сообщение об ошибке          str
"""
def get_leakage(file_path: str) -> Tuple[bool, Any]:
    success = True
    result = ""

    group_list = list()
    total_list = list()
    leakage_num = -1
    leakage = -1

    with open(file=file_path, mode='rt') as file:
        lines = file.read().split('\n')

        for line in lines:
            # Поиск номера столбца, содержащего информацию о Leakage Power
            if 'Group' in line and \
                    'Leakage' in line and not group_list:
                group_list = line.split()
                for num, item in enumerate(group_list):
                    if str(item) == 'Leakage':
                        leakage_num = num
                continue
            
            #  Получение значения утечки мощности в столбце Leakage Powre по его номеру
            if 'Total' in line and group_list:
                total_list = line.split()
                leakage = float(total_list[leakage_num])
                break

        # Обработка ошибок
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


""""
Образец искомого фрагмента входного файла

======================= Typical Corner ===================================

Group                  Internal  Switching    Leakage      Total
                          Power      Power      Power      Power (Watts)
----------------------------------------------------------------
Sequential             3.53e-04   6.66e-05   7.46e-10   4.20e-04  44.4%
Combinational          3.01e-04   2.24e-04   1.90e-09   5.26e-04  55.6%
Macro                  0.00e+00   0.00e+00   0.00e+00   0.00e+00   0.0%
Pad                    0.00e+00   0.00e+00   0.00e+00   0.00e+00   0.0%
----------------------------------------------------------------
Total                  6.55e-04   2.91e-04   2.65e-09   9.46e-04 100.0%
                          69.2%      30.8%       0.0%
"""