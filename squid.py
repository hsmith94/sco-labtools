import sys
import numpy as np
import os
import common as com
import csv

NUM_HEADER_LINES = 31

SAMPLE_NAME = ''    # Fe (Htrz)$_2$ (trz) $\cdot$ Bf$_4$'
LEGEND_KEY = ''     # '['25$\degree$C', '75$\degree$C', '100$\degree$C', '123$\degree$C', '128$\degree$C', '133$\degree$C', '138$\degree$C', '143$\degree$C', '148$\degree$C', '160$\degree$C']
# RELATIVE_MASS = ''  #348.84  # in grams per mole
# FIELD = '' #   1000.0   # in oersted
# MASS = ''  #   0.018215  # in grams

def specify(quantity, name, required=False):
    if not required:
        mode = 'Optional: '
    else:
        mode = ''
    print('\t{}Please specify {} in the config file using the keyword, "{}".'.format(mode, quantity, name))
    return True

def get_dirpath_from_user():
    while True:
        print('You must supply the directory path, not the file path.')
        input_path = com.get_path()
        if os.path.isdir(input_path):
            return input_path

if __name__ == '__main__':

    com.print_running_message(__file__)

    # FILE IO. Reading input and output paths from command line. Called using 'flags' such as:
    #
    #    >> path/to/file/SCOLabTools/squid.py -i path/to/input/dir/ -o path/to/output/dir
    #
    # Note that the input directory is required but the output directory is not, as outlined in com.io_from_args().
    #
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', action='store', dest='input', help='input path')
    parser.add_argument('-o', '--output', action='store', dest='output', help='output path')

    args = parser.parse_args()
    input_path, output_path = com.io_from_args(args)    # Read the IO command line arguments.
    config = com.read_config(output_path, loud=True)    # Read `config.yaml` from the input path.

    # READING CALCULATION QUANTITIES. Each of the required calculation quantities must be specified in the config
    # file. If quantities are not specified in the config, the code will flag a specification as missing and will exit
    # running until the quantity is specified.
    #
    spec_missing = False
    try:
        relative_mass = config['relmass']
    except:
        spec_missing = specify('relative mass (in grams per mole)', 'relmass', required=True)
        relative_mass = None
        # relative_mass = RELATIVE_MASS
    try:
        mass = config['mass']
    except:
        spec_missing = specify('sample mass (in grams)', 'mass', required=True)
        mass = None
        # mass = MASS
    # try:
    #     field = config['field']
    # except:
    #     specify('field strength (in oersted)', 'field', required=False)
    #     field = None
    #     # field = FIELD
    if spec_missing:
        exit(1)

    # file read-in
    from itertools import islice
    data_array = []
    for root, dirs, files in os.walk(input_path):
        for file in files:
            data = []
            if not os.path.splitext(file)[1] == '.dat':  # only select text files
                continue
            input_path = os.path.join(root, file)
            with open(input_path, 'r') as fh:
                text_file = csv.reader(fh, delimiter='\t')
                for line in islice(text_file, NUM_HEADER_LINES, None):
                    line_ = []
                    for element in line:
                        if element == '':
                            element = 0.0
                        element = float(element)
                        line_.extend((element,))
                    data.append(line_)
            data_array.append(data)

    data_array = data_array[0]
    data_array = np.array(data_array)

    long_moment = []
    temperature = []
    for data_point in data_array:
        temperature.append(data_point[3])
        long_moment.append(data_point[4])
    long_moment = np.array(long_moment)
    temperature = np.array(temperature)
    field_ = data_array[:, 2]
    field = np.mean(field_)     # This will take an average of the whole field.

    chi_MT = long_moment * temperature * relative_mass / ( field * mass )

    # plotting
    import matplotlib.pyplot as plt
    # maxlen = len(temperature)
    # j = 0
    # k = 0
    # for i, _ in enumerate(temperature):
    #     if i == 0:  # there is no i-1
    #         continue
    #     if i == maxlen - 1:   # there is no i+1
    #         continue
    #     a = temperature[i-1]
    #     b = temperature[i]
    #     c = temperature[i+1]
    #     if a >= b:   # plot was decreasing
    #         if c > b:    # plot is now increasing
    #             k = i
    #             plt.plot(temperature[j:k], chi_MT[j:k])
    #             j = k
    # plt.plot(temperature[k:], chi_MT[k:])
    com.plot_hysteresis(plt, temperature, chi_MT)

    # plt.plot(temperature, chi_MT)
    # plotting arrows
    significance_threshold = 0.02
    shrink = 40
    for i, _ in enumerate(chi_MT):
        max = np.shape(chi_MT)[0]
        if i < max - 1:
            Dchi_MT = chi_MT[i+1] - chi_MT[i]
            if abs(Dchi_MT) > significance_threshold:
                ax = plt.axes()
                ax.annotate('', xy=(temperature[i+1], chi_MT[i+1]), xytext=(temperature[i], chi_MT[i]),
                            arrowprops=dict(arrowstyle='->', linestyle=None, color='k', shrinkA=shrink, shrinkB=shrink))

                # Dtemperature = temperature[i+1] - temperature[i]
                # ax.arrow(temperature[i], chi_MT[i], Dtemperature, Dchi_MT, head_width=0.005, head_length=0.01,)

    plt.ylabel('Weighted Magnetic Susceptibility $\chi_M\,T$ [K$^{-1}$]')
    plt.xlabel('Temperature [K]')

    com.saveplot(plt, output_path, 'graph.png')
    com.saveplot(plt, output_path, 'graph.pdf')
    com.saveplot(plt, output_path, 'graph.svg')

    plt.show()
