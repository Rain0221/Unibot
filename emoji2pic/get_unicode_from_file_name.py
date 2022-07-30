import os


def organize_file_name(file_dir='AppleEmoji'):
    """
    从emoji图片文件名整理出对应的Unicode
    GET Unicode from file name
    """
    for root, dirs, files in os.walk(file_dir):
        pass

    unicode_to_path = dict()
    initial_unicode = dict()

    for file in files:
        chip_list = file.split('_')
        eng = len(chip_list[0]) + 1 if chip_list[1][:5] != 'emoji' else len(chip_list[0] + chip_list[1]) + 2
        base_name = file[eng:-4].replace('_', '-')
        base_name_chip_list = base_name.split('-')

        keycap = False
        unicode_chip_list = list()
        for chip in base_name_chip_list:
            if len(chip) == 2:
                if chip in ('23', '2a', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39',):
                    keycap = True
                unicode_chip = u'\\x' + chip
            elif len(chip) == 4:
                unicode_chip = u'\\u' + chip
            elif len(chip) == 5:
                unicode_chip = u'\\U000' + chip
            else:
                raise ValueError(chip)
            unicode_chip_list.append(unicode_chip.encode('utf-8').decode('unicode_escape'))

        if initial_unicode.get(unicode_chip_list[0]) is None:
            initial_unicode[unicode_chip_list[0]] = [len(unicode_chip_list)]
        else:
            if len(unicode_chip_list) not in initial_unicode[unicode_chip_list[0]]:
                initial_unicode[unicode_chip_list[0]].append(len(unicode_chip_list))
                initial_unicode[unicode_chip_list[0]] = sorted(initial_unicode[unicode_chip_list[0]], reverse=True)

        unicode_name = ''.join(unicode_chip_list)
        unicode_to_path[unicode_name] = file

        if keycap is True:  # 数字emoji
            initial_unicode[unicode_chip_list[0]].append(2)
            keycap_unicode_name = ''.join([unicode_chip_list[0], unicode_chip_list[2]])
            unicode_to_path[keycap_unicode_name] = file

    with open('emoji_directory.py', 'w', encoding='utf8') as f:
        f.write('INITIAL_UNICODE = ' + str(initial_unicode) + '\n'+'UNICODE_TO_PATH = '+str(unicode_to_path)+'\n')

    return


if __name__ == '__main__':
    organize_file_name()
