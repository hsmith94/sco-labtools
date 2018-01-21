import common as com
import os

FILENAME = 'Test_5A_Sample_A1'
OLD_FILENAME = 'image'
BASE_NUM = 213
OUTPUT_FOLDER = 'fixed'

if __name__ == '__main__':

    print("Running `{}`.".format(os.path.split(__file__)[1]))

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', action='store', dest='input', help='input path')

    args = parser.parse_args()
    # input path validation
    input_path = args.input
    if input_path is None:
        input_path = com.get_path()
    elif not os.path.exists(input_path):  # if `input_path` does not exist
        input_path = com.get_path()

    import re
    for root, dirs, files in os.walk(input_path):
        for i, file in enumerate(files):
            filesplit = os.path.splitext(file)
            filename = filesplit[0]
            fileext = filesplit[1]

            file_path = os.path.join(root, file)
            match = re.match(r"([a-z]+)([0-9]+)", filename, re.I)
            if match:
                text, num = match.groups()
                num = int(num)
                num = num + BASE_NUM
                new_file_name = "{}{}{}".format(FILENAME, num, fileext)
                # new_root = os.path.join(root, OUTPUT_FOLDER)
                new_root = root
                com.if_not_exists_create_dir(new_root)
                new_file_path = os.path.join(new_root, new_file_name)
                if text == OLD_FILENAME:
                    os.rename(file_path, new_file_path)