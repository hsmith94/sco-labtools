def celsius_to_kelvin(temperature):
    import numpy as np
    temperature = np.asarray(temperature)
    temperature = temperature + 273.15
    temperature = list(temperature)
    return temperature

def compress_to_roi(img_arr, roi, percentage=50):
    from scipy.misc import imresize
    # unpacking roi
    roi_x0, roi_y0, roi_x1, roi_y1 =  roi[0], roi[1], roi[2], roi[3]
    img_arr = img_arr[roi_x0:roi_x1, roi_y0:roi_y1, :]  # preserves RGB color
    img_arr = imresize(img_arr, percentage)
    return img_arr

def draw_roi(img_arr, filename, output_path, roi):
    from PIL import Image
    import os
    from colour import Color
    import sys

    sys.stdout.write('\rProducing ROI image file... ')
    sys.stdout.flush()
    # unpacking roi
    roi_x0, roi_y0, roi_x1, roi_y1 =  roi[0], roi[1], roi[2], roi[3]
    # creating output path
    file_output_path = os.path.join(output_path, "{}_roi.png".format(os.path.splitext(filename)[0]))
    if_not_exists_create_file(file_output_path)
    # drawing on image
    c = Color('yellow')  # not sure why the yellow color isn't working
    col = c.rgb
    col = list(col)
    stroke = 2
    img_arr[roi_x0 - stroke:roi_x0 + stroke, roi_y0:roi_y1] = col
    img_arr[roi_x1 - stroke:roi_x1 + stroke, roi_y0:roi_y1] = col
    img_arr[roi_x0:roi_x1, roi_y0 - stroke:roi_y0 + stroke] = col
    img_arr[roi_x0:roi_x1, roi_y1 - stroke:roi_y1 + stroke] = col
    # saving image
    im = Image.fromarray(img_arr)
    im.save(file_output_path)
    sys.stdout.write("\rROI image output to {}\n".format(file_output_path))
    sys.stdout.flush()
    return

def get_image_dims(path):
    from PIL import Image
    im = Image.open(path)
    width, height = im.size
    dims = width, height
    return dims

def get_path(path_type='Input'):
    import os
    path = None
    loops = 0
    while True:  # loop until valid input given
        loops = loops + 1
        path = input('Please provide an {} path: '.format(path_type.lower()))  # get user to supply input path
        # remove quote marks
        path = path.replace('"', '')
        path = path.replace("'", "")
        # input validation
        if path == 'help':
            print('\tHelp: {} path is the folder where you have all the JPEG image files (.jpg) from your reflectivity experiment.'.format(path_type))
        elif path == 'exit':
            exit(0)
        elif not os.path.exists(path):    # check path exists
            print('\tPath does not exist.')
            if loops >= 3:
                print('\tPlease note: Path cannot contain any special characters.')
        else:   # accept input
            break
    return path

def if_not_exists_create_dir(dir):
    import os
    if not os.path.exists(dir):    # create directory structure
        os.makedirs(dir)
        # print('Successfully created directory {}!'.format(dir))

def if_not_exists_create_file(path):
    import os
    root = os.path.split(path)[0]
    if_not_exists_create_dir(root)
    if not os.path.exists(path):    # create file
        open(path, 'a').close()
        # print('Successfully created file {}!'.format(path))

def io_from_args(args):
    input_path = validate_input_path(args.input)
    output_path = validate_output_path(args.output, input_path)
    return input_path, output_path

def longest(l):
    '''
    Finds length longest list within a list of lists `l`.
    :param l:
    :return:
    '''
    if(not isinstance(l, list)): return(0)
    return(max([len(l),] + [len(subl) for subl in l if isinstance(subl, list)] +
        [longest(subl) for subl in l]))

def make_output_folder_in_current_dir(dir, name='output'):
    import os
    output_path = os.path.join(dir, name)
    if_not_exists_create_dir(output_path)
    print('Output path set to {}.'.format(output_path))
    return output_path

def normalize(X, min=None, max=None):
    if min is None:
        min = X.min()
    if max is None:
        max = X.max()
    X_norm = (X - min)/(max - min)
    return X_norm

def plot_hysteresis(plt, x, y, format='-', legend=True):
    def update_legend(lgnd, num):
        label = 'Loop {}'.format(num)
        lgnd.append(label)

    maxlen = len(x)
    j = 0
    k = 0
    f = []
    lgnd = []
    lnum = 0 # loop count
    for n, _ in enumerate(x):
        if n == 0:  # there is no i-1
            continue
        if n == maxlen - 1:  # there is no i+1
            continue
        a = x[n - 1]
        b = x[n]
        c = x[n + 1]
        if a < b < c:
            f = 'increasing'
        elif a > b > c:
            f = 'decreasing'
        # f will not update during a 'hold' or 'wait'
        if c > b and f == 'decreasing':
            lnum += 1
            k = n
            plt.plot(x[j:k], y[j:k], format)
            update_legend(lgnd, lnum)
            j = k
    plt.plot(x[k:], y[k:], format)
    update_legend(lgnd, lnum+1)
    if legend:
        plt.legend(lgnd)
    return plt

def print_running_message(name):
    import os
    print("Running `{}`.".format(os.path.split(name)[1]))

def print_progress(iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    """
    Call in a loop to create terminal progress bar
    SOURCE: http://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    import sys
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    sys.stdout.write('\r{} |{}| {} {}'.format(prefix, bar, percent, suffix))
    sys.stdout.flush()
    # print new line on completion
    if iteration == total:
        print()

def read_config(yaml_dir, yaml_fname='config.yaml', loud=False):
    import os
    yaml_path = os.path.join(yaml_dir, yaml_fname)
    try:
        config = read_yaml(yaml_path)
        return config
    except:
        if loud:
            recommendation('provide a `{}` file in the `{}` directory'.format(yaml_fname, yaml_dir))
        return

def read_yaml(yaml_path):
    import yaml
    with open(yaml_path, 'r') as fh:
        try:
            yaml_ = yaml.load(fh)
            return yaml_
        except yaml.YAMLError as exc:   # error handling
            print(exc)
            return

def recommendation(str):
    str = str.lower()
    print("\tIt is recommended that you {}. Please refer to the user manual for details.".format(str))
    return False

def saveplot(plt, output_path, file_name, printmessage=False):
    import os
    file_output_path = os.path.join(output_path, file_name)
    if_not_exists_create_file(file_output_path)
    plt.savefig(file_output_path)
    if printmessage:
        print('Figure output to {}.'.format(file_output_path))

def transpose_list(l):
    # only works on 2-D list
    import itertools as it
    list(map(list, it.zip_longest(*l)))

def validate_input_path(input_path):
    import os
    if input_path is None:
        input_path = get_path()
    elif not os.path.exists(input_path):  # if `input_path` does not exist
        input_path = get_path()
    return input_path

def validate_output_path(output_path, input_path):
    import os
    if output_path is None:
        output_path = make_output_folder_in_current_dir(input_path)
    elif not os.path.exists(output_path):  # if `output_path` does not exist
        output_path = make_output_folder_in_current_dir(input_path)
    return output_path
