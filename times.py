import common as com
import os
import csv

OUTPUT_FILE_NAME = 'times.dat'

def get_creation_date(path):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    import os
    import platform

    if platform.system() == 'Windows':
        return os.path.getctime(path)
    else:
        stat = os.stat(path)
        try:
            return stat.st_birthtime    # only available on MAC OS
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime

def diff_times(t1, t2):
    return t2 - t1

if __name__ == '__main__':

    com.print_running_message(__file__)

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', action='store', dest='input', help='input directory path')

    args = parser.parse_args()
    # input path validation
    input_path = args.input
    if input_path is None:
        input_path = com.get_path()
    elif not os.path.exists(input_path):  # if `input_path` does not exist
        input_path = com.get_path()
    # output path
    output_path = com.make_output_folder_in_current_dir(input_path)

    output_file_path = os.path.join(output_path, OUTPUT_FILE_NAME)
    com.if_not_exists_create_file(output_file_path)
    with open(output_file_path, 'w') as csv_file:
        writer = csv.writer(csv_file, delimiter='\t')
        for root, dirs, files in os.walk(input_path):
            i = 0
            first_file = True
            first_date = 0.0
            for j, file in enumerate(files):
                # if file is a jpg
                ext = os.path.splitext(file)[1].lower()
                if ext == '.jpg':
                    # read dates
                    input_file_path = os.path.join(root, file)
                    date = get_creation_date(input_file_path)
                    # calculate differences
                    if first_file:
                        first_date = date
                        first_file = True
                    diff = diff_times(first_date, date) # in seconds

                    # write dates to file
                    row = [i, date, diff]
                    writer.writerow(row)

                    # counter increment
                    i += 1