import sys
import numpy as np
import os

from scipy import ndimage
from scipy import misc

import common as com

TIMES_FILENAME = 'times.dat'
CURVE_FILENAME = 'curve.dat'
ROI_FILENAME = 'roi.dat'
OUTPUT_FILENAME = 'data.dat'

IMGDT = 60.0    # seconds
SAMPLE_NAME = '' # example: 'Fe (Htrz)$_2$ (trz) $\cdot$ Bf$_4$'

def get_dims_from_dummy_file(path):
    w = 200 # arbitrary fallback
    h = 200 # arbitrary fallback
    for rt, _, fs in os.walk(path):
        while True:
            for f in fs:
                ext = os.path.splitext(f)[1].lower()
                if ext == '.jpg':
                    in_path = os.path.join(rt, f)
                    w, h = com.get_image_dims(in_path)
                    break
                else:
                    continue
            break
    return w, h

def get_roi(input_path, config={}):
    # try config
    if config == {}:
        config = com.read_config(input_path)
    roi = get_roi_from_config(config)
    # try file
    if roi == []:
        roi = get_roi_from_file(input_path)
    # try image
    if roi == []:
        roi = get_roi_from_img(input_path)
    return roi

def get_roi_from_config(config):
    # defining the region of interest
    roi = []
    try:
        roi = config['roi']
        print('\tUsing ROI from config as {}'.format(roi))
    except:
        pass
    return roi

def get_roi_from_file(input_path):
    import csv
    roi = []
    roi_file_path = os.path.join(input_path, 'output', ROI_FILENAME)
    try:
        with open(roi_file_path) as roi_file:
            reader = csv.reader(roi_file, delimiter='\t')
            for line in reader:
                X0, Y0, W = [int(el) for el in line]
                roi = [X0, Y0, X0 + W, Y0 + W]
        print('\tUsing ROI from file {} as {}'.format(roi_file_path, roi))
    except:
        pass
    return roi

def get_roi_from_img(input_path):
    width, height = get_dims_from_dummy_file(input_path)
    roi = get_roi_from_dims(width, height, window = 300)
    print('\tUsing ROI from image dimensions as {}'.format(roi))
    return roi

def get_roi_from_dims(w, h, window=200):
    x0 = int((w - window) / 2)
    y0 = int((h - window) / 2)
    x1 = int((w + window) / 2)
    y1 = int((h + window) / 2)
    roi = list([x0, y0, x1, y1])
    return roi

def is_jpeg(f):
    import os
    ext = os.path.splitext(f)[1].lower()
    if ext == '.jpg':
        return True
    else:
        return False

if __name__ == '__main__':

    com.print_running_message(__file__)

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', action='store', dest='input', help='input path')
    parser.add_argument('-o', '--output', action='store', dest='output', help='output path')

    args = parser.parse_args()
    input_path, output_path = com.io_from_args(args)
    config = com.read_config(output_path)

    # get roi
    roi = get_roi(input_path, config=config)

    # read file creation times from file
    import csv
    times_file_path = os.path.join(input_path, 'output', TIMES_FILENAME)
    try:
        times = []
        first_time = 0.0
        read_first_time = False
        with open(times_file_path, 'r') as fh:
            reader = csv.reader(fh, delimiter='\t')
            for i, line in enumerate(reader):
                if line == []:
                    continue
                time = line[2]
                time = float(time)
                if not read_first_time:
                    first_time = time
                    read_first_time = True
                diff = time - first_time
                times.append(diff)
    except:
        com.recommendation('produce a `{}` file and provide it in the `./output` directory'.format(TIMES_FILENAME))
        times = []
        # trying the config for pre-defined temperatures (last resort)
        try:
            temps = config['temperatures']
        except:
            temps = []

    try:
        imgdt = config['imgdt']
    except:
        imgdt = IMGDT

    try:
        sample = config['sample']
    except:
        sample = SAMPLE_NAME


    try:
        if times != []:
            import curve
            curves_file_path = os.path.join(input_path, 'output', CURVE_FILENAME)
            curve_profile = curve.get_curve(curves_file_path)  # read temperature curve file
            temps = []
            curve_pts = curve.get_curve_points(curve_profile)   # get points from curve
            T = curve.interp_points(curve_pts)  # interpolate points into function
            for t in times: # for each given time, find corresponding temperature
                t = t / 60.0   # from seconds to minutes
                Tt = T(t)
                temps.append(Tt)
    except:
        com.recommendation('provide a `{}` file in the `./output` directory'.format(CURVE_FILENAME))
        pass

    # convert temperatures to kelvin
    temps = com.celsius_to_kelvin(temps)

    plot_array = []
    written_roi_image = False
    pfx = 'Analysing data. Progress:'
    for root, dirs, files in os.walk(input_path):
        for i, file in enumerate(files):
            # if file is a jpeg
            if is_jpeg(file):
                # read image
                file_input_path = os.path.join(root, file)
                image = ndimage.imread(file_input_path)
                # draw roi onto dummy image for user visualization
                if not written_roi_image:  # use first image as dummy file
                    com.draw_roi(image, file, output_path, roi)
                    written_roi_image = True
                # update progress message
                com.print_progress(i, len(files) - 1, prefix=pfx, length=40)
                # compress image to speed up
                image = com.compress_to_roi(image, roi, percentage=50)
                # extract color data
                R, G, B = np.mean(image[:, :, 0]), np.mean(image[:, :, 1]), np.mean(image[:, :, 2])
                I = (R + G + B) / 3.   # intensity
                # TODO: Speed up code: save values to file, use separate code to plot
                plot_array.append([R, G, B, I])
    sys.stdout.write('\r{} Completed.{}'.format(pfx, ''*15))
    print()

    print('Plotting data...')
    # normalization
    plot_array = np.asarray(plot_array)
    # find min and max of `plot_array`
    plot_array_min = plot_array.min()
    plot_array_max = plot_array.max()
    # give `normalize()` function these values for each RGBI
    R_norm = com.normalize(plot_array.T[0], min=plot_array_min, max=plot_array_max)
    G_norm = com.normalize(plot_array.T[1], min=plot_array_min, max=plot_array_max)
    B_norm = com.normalize(plot_array.T[2], min=plot_array_min, max=plot_array_max)
    I_norm = com.normalize(plot_array.T[3], min=plot_array_min, max=plot_array_max)
    R_norm, G_norm, B_norm, I_norm = np.ndarray.tolist(R_norm), np.ndarray.tolist(G_norm), np.ndarray.tolist(B_norm), np.ndarray.tolist(I_norm)
    plot_array = [R_norm, G_norm, B_norm, I_norm]

    I_norm = np.asarray(I_norm)
    I_array = com.normalize(I_norm)

    B_norm = np.asarray(B_norm)
    B_array = com.normalize(B_norm)

    # plotting
    import matplotlib.pyplot as plt
    plt.figure(1)
    k = plot_array[3]
    r = plot_array[0]
    g = plot_array[1]
    b = plot_array[2]
    if temps == []:    # if temperature range is empty
        plt.plot(k, 'k--')
        plt.plot(r, 'r')
        plt.plot(g, 'g')
        plt.plot(b, 'b')
        plt.xlabel('Image number')
    else:
        plt.plot(temps, k, 'k--')
        plt.plot(temps, r, 'r')
        plt.plot(temps, g, 'g')
        plt.plot(temps, b, 'b')
        plt.xlabel('Temperature')
    plt.title('Reflectivity for {}'.format(SAMPLE_NAME))
    plt.ylabel('Normalised intensity')
    plt.legend(['Gray', 'R', 'G', 'B'])

    plt.figure(2)
    k = I_array
    form = 'o-'
    if temps == []:    # if temperature range is empty
        plt.plot(k, form)
        plt.xlabel('Image number')
    else:
        com.plot_hysteresis(plt, temps, k, format=form)
        plt.xlabel('Temperature [K]')
    plt.title('Reflectivity for {}'.format(SAMPLE_NAME))
    plt.ylabel('Normalised intensity')
    plt.legend(['Loop 1', 'Loop 2', 'Loop 3'])
    # file output
    com.saveplot(plt, output_path, 'graph_k.pdf')
    com.saveplot(plt, output_path, 'graph_k.png')
    com.saveplot(plt, output_path, 'graph_k.svg')

    plt.figure(3)
    b = B_array
    form = 'o-'
    if temps == []:    # if temperature range is empty
        plt.plot(b, form)
        plt.xlabel('Image number')
    else:
        com.plot_hysteresis(plt, temps, b, format=form)
        plt.xlabel('Temperature [K]')
    plt.title('Blue Intensity for {}'.format(SAMPLE_NAME))
    plt.ylabel('Normalised intensity')
    plt.legend(['Loop 1', 'Loop 2', 'Loop 3'])
    # file output
    com.saveplot(plt, output_path, 'graph_b.pdf')
    com.saveplot(plt, output_path, 'graph_b.png')
    com.saveplot(plt, output_path, 'graph_b.svg')

    # write data to file
    output_file_path = os.path.join(output_path, OUTPUT_FILENAME)
    imgdt_ = imgdt / 60.0
    with open(output_file_path, 'w+') as fh:
        writer = csv.writer(fh, delimiter='\t', lineterminator='\n')
        # header
        writer.writerow(['[HEADER]'])
        writer.writerow(['Sample name:', sample])
        writer.writerow(['Time between photos: [mins]', imgdt_])
        writer.writerow(['Curve profile:'])
        writer.writerows(curve_profile)
        # data
        writer.writerow(['[DATA]'])
        writer.writerow(['i', 't [mins]', 'T [deg C]', 'R', 'G', 'B', 'k'])
        times_ = [t / 60.0 for t in times]  # conversion to minutes
        for i, _ in enumerate(times_):
            writer.writerow([i, times_[i], temps[i], r[i], g[i], b[i], k[i]])
    print('Data output to {}'.format(output_file_path))

    # screen output
    plt.show()