import os

def get_leakage(file_path: str) -> float:
    group_list = list()
    total_list = list()
    leakage_num = -1
    leakage = -1

    if not os.path.exists(file_path):
        print("get leakage step:\n\tfatal: input file does not exist\n\texiting")
        exit()

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
            print("get leakage step:\n\tfatal: Group line not found\n\texiting")
            exit()
        if not total_list:
            print("get leakage step:\n\tfatal: Total line not found\n\texiting")
            exit()

    if leakage == -1:
        print("get leakage step:\n\tfatal: leagake not found\n\texiting")
        exit()
    else:   
        return leakage