import os
import re
import math


def parse_indices(data_dir):
    """
    Parse indices from a parallel .lib files to find indices of different lines.
    This is a same line (by index) from different files. So this func will add this index to the return list.

    50: values("0.51486,0.51811,0.52672,0.54899,0.61469,0.82888,1.54291");
    50: values("0.83935,0.84259,0.85120,0.87348,0.93916,1.15333,1.86705");

    data_dir: input data directory

    return indices of different strings.
    """
    data = os.listdir(data_dir)

    all_data_indices = set()
    lib_sample = open(data_dir + '/' + data[0])
    for count, line in enumerate(lib_sample):
        if re.search('values', line):
            all_data_indices.add(count)

    all_data_indices = list(all_data_indices)
    all_data_indices.sort()
    return all_data_indices


def merge(data_dir, data_to, diff_lines, net_transitions):
    """
    Main function of a file.
    Merge files by indices of different lines.
    data_dir: input data directory
    data_to: output data directory
    diff_lines: indices of different lines
    net_transitions: net transition
    """
    data = os.listdir(data_dir)
    lib_sample = open(data_dir + '/' + data[0])
    merged_data = {}

    indices_scalar = []

    data = sorted(data)

    for i, line in enumerate(lib_sample):
        if i in diff_lines:
            line = line.replace(' ', '')
            if re.search(r'"[-+]?\d*\.*\d+"', line):
                indices_scalar.append(i)

    for index in diff_lines:
        merged_data[index] = []

    for index in indices_scalar:
        if index in diff_lines:
            diff_lines.remove(index)

    for file_name in data:
        for count, line in enumerate(open(data_dir + '/' + file_name)):
            if count in indices_scalar:
                tmp = re.search(r'"[-+]?\d*\.*\d+"', line).group(0)[1:-1] + ', '

                merged_data[count].append(tmp)

    tmp = ['']
    cnt = 0
    for key in indices_scalar:
        col_data_len = int(len(net_transitions))
        len_data = len(merged_data[key])
        row_data_len = len_data / col_data_len
        for counter, item in enumerate(merged_data[key]):
            if (((counter + 1) % row_data_len) == 0) and (counter != 0):
                merged_data[key][counter] = merged_data[key][counter][0:-1]
                if ((counter + 1) % len_data) != 0:
                    merged_data[key][counter] = merged_data[key][counter][0:-1]
                    merged_data[key][counter] = merged_data[key][counter] + '", \ \n'
                else:
                    merged_data[key][counter] = merged_data[key][counter][0:-1] + '" \n'

            if (counter == 0) or (((counter + 1) % row_data_len) == 1):
                merged_data[key][counter] = '"' + merged_data[key][counter]

            tmp[cnt] = tmp[cnt] + merged_data[key][counter]
            if (((counter + 1) % row_data_len) == 0) and (counter != 0):
                cnt = cnt + 1
                tmp.append('')

        if len(tmp) > 1:
            merged_data[key] = tmp[0:-1]
        if len(merged_data[key]) > 0:
            merged_data[key][-1] = merged_data[key][-2] + ');'
        tmp = ['']
        cnt = 0

    for key in indices_scalar:
        if len(merged_data[key]) > 0:
            merged_data[key][0] = 'values 	( ' + merged_data[key][0]
            merged_data[key][-1] = merged_data[key][-1].replace(', \\ \n);', '");')

    for file_name in data:
        clk, clk_val, pin, pin_val = file_name[file_name.find('clk'):].split('_')

        if clk_val == pin_val[0:-4]:
            for count, line in enumerate(open(data_dir + '/' + file_name)):
                if count in diff_lines:
                    tmp = str()
                    tmp_arr = re.findall(r'[-+]?\d*\.*\d+', line)
                    tmp_arr[-1] = tmp_arr[-1] + '", \ \n'
                    tmp_arr[0] = '"' + tmp_arr[0]
                    for item in tmp_arr:
                        tmp = tmp + item + ', '

                    tmp = tmp[0:-2]
                    merged_data[count].append(tmp)

        if clk_val == 'NaN':
            for count, line in enumerate(open(data_dir + '/' + file_name)):
                if count in diff_lines:
                    tmp = str()
                    tmp_arr = re.findall(r'[-+]?\d*\.*\d+', line)
                    tmp_arr[-1] = tmp_arr[-1] + '", \ \n'
                    tmp_arr[0] = '"' + tmp_arr[0]
                    for item in tmp_arr:
                        tmp = tmp + item + ', '

                    tmp = tmp[0:-2]
                    merged_data[count].append(tmp)

    for key in merged_data:
        if len(merged_data[key]) > 0:
            merged_data[key][-1] = merged_data[key][-1][0:-4] + '); \n'

    for key in diff_lines:
        if len(merged_data[key]) > 0:
            merged_data[key][0] = 'values 	(' + merged_data[key][0]
            merged_data[key][-1] = merged_data[key][-1][0:-5] + '); \n'

    counter = 0
    new_lib = []
    lib_sample = open(data_dir + '/' + data[0])
    for i, line in enumerate(lib_sample):
        if i in merged_data:
            tmp = merged_data[i]
            counter = counter + len(merged_data[i])
        else:
            tmp = line
        new_lib.append(''.join(tmp))

    new_lib_file = open(data_to + '/tmp.lib', 'w')
    # print(new_lib_file)
    for line in new_lib:
        if re.search(r'scalar', line):
            tmp = line.replace('scalar', '%sample%')
        else:
            tmp = line
        new_lib_file.write(tmp)

    return merged_data


def tmp_clr(data_to):
    os.remove(data_to + '/tmp.lib')

# indices = parse_indices('data')
#
# test = merge('data', indices)
#
# print('aaaa')
# pass
