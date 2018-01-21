import common as com
import matplotlib.pyplot as plt
import os
import numpy as np

def get_xy(file):
    import csv
    import numpy as np
    x = []
    y = []
    with open(file, 'r') as fh:
        open_file = csv.reader(fh, delimiter='\t')
        for line in open_file:
            x_ = line[0]
            y_ = line[1]
            x_ = float(x_)
            y_ = float(y_)
            x.append(x_)
            y.append(y_)
    return x, y

def get_errors(file):
    import csv
    import numpy as np
    err = []
    with open(file, 'r') as fh:
        open_file = csv.reader(fh, delimiter='\t')
        for line in open_file:
            err_ = line[2]
            err_ = float(err_)
            err.append(err_)
    return err

def make_plot(plt, x, y, format_, config, hysteresis=False):
    if hysteresis:
        try:
            hyst_legend = config['legend']
        except:
            hyst_legend = True
        com.plot_hysteresis(plt, x, y, format=format_, legend=hyst_legend)
    else:
        plt.plot(x, y, format_)

if __name__ == '__main__':

    com.print_running_message(__file__)

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', action='store', dest='input', help='input path')
    parser.add_argument('-c', '--config', action='store', dest='config', help='config path')
    parser.add_argument('-o', '--output', action='store', dest='output', help='output path')

    args = parser.parse_args()
    # input
    input_path = args.input
    if input_path is None:
        input_path = com.get_path('Input')
    if not os.path.isfile(input_path):
        print('{} is not a valid input file.'.format(input_path))
        input_path = com.get_path('Input')
    input_file = input_path
    input_dir = os.path.split(input_file)[0]
    # output
    output_path = args.output
    if output_path is None:
        output_path = input_dir
    # config
    config_path = args.config
    if config_path is None:
        config_path = com.get_path('Config')
    if not os.path.isfile(config_path):
        print('{} is not a valid config file.'.format(config_path))
        config_path = com.get_path('Config')
    config = com.read_yaml(config_path)

    # read data
    x, y = get_xy(input_file)

    try:
        normalize = config['norm']
        if normalize:
            print('Normalizing data.')
            y = np.asarray(y)
            y = com.normalize(y)
    except:
        pass

    # # dummy data
    # x = range(0,10)
    # y = np.asarray(x) ** 3

    # plotting
    plt.figure(1)
    try:
        format_ = config['format']
    except:
        format_ = '-'
    try:
        hysteresis = config['hysteresis']
    except:
        hysteresis = False
    make_plot(plt, x, y, format_, config, hysteresis=hysteresis)
    try:
        plottwo = config['plottwo']
    except:
        plottwo = False
    if plottwo:
        try:
            input_file2 = config['plottwofp']
        except:
            input_file2 = None
        if input_file2 is None:
            input_file2 = com.get_path('Second input')
        x2, y2 = get_xy(input_file2)
        make_plot(plt, x2, y2, format_, config, hysteresis=hysteresis)

    # TODO: Combine these statements to fix color
    try:
        error_provided_in_file = config['errorprovided']
    except:
        error_provided_in_file = False
    if error_provided_in_file:
        errors = get_errors(input_file)
        plt.errorbar(x, y, yerr=errors, fmt='b{}'.format(format_))
        if plottwo:
            errors2 = get_errors(input_file2)
            plt.errorbar(x2, y2, yerr=errors2, fmt='b{}'.format(format_))
    try:
        yerror = config['yerror']
    except:
        yerror = None
    if yerror is not None:  # TODO: Allow x error
        plt.errorbar(x, y, yerr=yerror, fmt='b{}'.format(format_))
    # FORMATTING
    try:
        grid = config['grid']
        if grid:
            plt.grid(b=True, which='major', color='0.50', linestyle='-')
            plt.grid(b=True, which='minor', color='0.25', linestyle='--')
    except:
        pass
    try:
        biglabels = config['biglabels']
    except:
        biglabels = False
    if biglabels:
        from matplotlib import rc
        font = {'size': 20}
        rc('font', **font)
    try:
        title = config['title']
    except:
        title = None
    if title is not None:
        plt.title(title)
    try:
        xlabel = config['xlabel']
    except:
        xlabel = None
    if xlabel is not None:
        plt.xlabel(xlabel)
    try:
        ylabel = config['ylabel']
    except:
        ylabel = None
    if ylabel is not None:
        plt.ylabel(ylabel)
    try:
        fitline = config['fitline']
    except:
        fitline = False
    if fitline:
        # include line
        try:
            a_ = config['a']
            b_ = config['b']
            x0, xspan = config['linerange']
        except:
            a_ = None
            b_ = None
            x0 = None
            xspan = None
            print('Could not fit line. Please provide `a` and `b` for y = ax + b in `config.yaml`.')
        if a_ is not None and b_ is not None:
            if x0 is None:
                x0 = 0
            if xspan is None:
                xspan = 100
            x_ = range(x0, xspan, 1)
            x_ = np.asarray(x_)
            y_ = a_ * x_ + b_
            plt.plot(x_, y_, color='b')
            plt.axvline(0, color='k')
    try:
        fitline2 = config['fitline2']
    except:
        fitline2 = False
    if fitline2:
        # include line
        try:
            a2_ = config['a2']
            b2_ = config['b2']
            x20, x2span = config['linerange2']
        except:
            a2_ = None
            b2_ = None
            x20 = None
            x2span = None
            print('Could not fit line. Please provide `a2` and `b2` for y2 = a2x2 + b2 in `config.yaml`.')
        if a2_ is not None and b2_ is not None:
            if x20 is None:
                x20 = 0
            if x2span is None:
                x2span = 100
            x2_ = range(x20, x2span, 1)
            x2_ = np.asarray(x2_)
            y2_ = a2_ * x2_ + b2_
            plt.plot(x2_, y2_, color='b')
            plt.axvline(0, color='k')
    # fit exponential
    try:
        fitexp = config['fitexp']
    except:
        fitexp = False
    if fitexp:
        try:
            a_ = config['a']
            b_ = config['b']
            x0, xspan = config['linerange']
        except:
            a_ = None
            b_ = None
            x0 = None
            xspan = None
            print('Could not fit line. Please provide `a` and `b` for y = ax + b in `config.yaml`.')
        if a_ is not None and b_ is not None:
            if x0 is None:
                x0 = 0
            if xspan is None:
                xspan = 100
            x_ = range(x0, xspan, 1)
            x_ = np.asarray(x_)
            y_ = a_ * np.exp(b_ * x_)
            plt.plot(x_, y_, color='b')
            plt.axvline(0, color='k')
    # output
    try:
        outname = config['outname']
        outexts = config['outexts']
    except:
        outname = 'graph'
        outexts = ['.png', '.svg']

    for ext in outexts:
        outfile = '{}{}'.format(outname, ext)
        com.saveplot(plt, output_path, outfile, printmessage=True)

    plt.show()
