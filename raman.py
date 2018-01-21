import sys
import numpy as np
import os
import common as com
import csv

SAMPLE_NAME = 'Fe (Htrz)$_2$ (trz) $\cdot$ Bf$_4$'
LEGEND_KEY = ['25$\degree$C', '75$\degree$C', '100$\degree$C', '123$\degree$C', '128$\degree$C', '133$\degree$C', '138$\degree$C', '143$\degree$C', '148$\degree$C', '160$\degree$C']
PLT_SHIFT = 0.5
SNR_FACTOR = 0.2

PEAKS_OUTPUT_FILENAME = 'peaks.dat'

if __name__ == '__main__':

    com.print_running_message(__file__)

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', action='store', dest='input', help='input path')
    parser.add_argument('-o', '--output', action='store', dest='output', help='output path')

    args = parser.parse_args()
    # input path validation
    input_path = args.input
    if input_path is None:
        input_path = com.get_path()
    elif not os.path.exists(input_path):  # if `input_path` does not exist
        input_path = com.get_path()
    # output path validation
    output_path = args.output
    if output_path is None:
        output_path = com.make_output_folder_in_current_dir(input_path)
    elif not os.path.exists(output_path):  # if `output_path` does not exist
        output_path = com.make_output_folder_in_current_dir(input_path)

    # file read-in
    data_array = [] # NOTE THIS ONLY WORKS FOR ONE DIRECTORY AT A TIME
    for root, dirs, files in os.walk(input_path):
        for file in files:
            data = []
            if not os.path.splitext(file)[1] == '.txt':  # only select text files
                continue
            input_path = os.path.join(root, file)
            with open(input_path, 'r') as fh:
                text_file = csv.reader(fh, delimiter='\t')
                for line in text_file:
                    line_ = []
                    for element in line:
                        element = float(element)
                        line_.extend((element,))
                    data.append(line_)
            data_array.append(data)
    data_array = np.asarray(data_array)

    # normalization
    data_array_ = []
    for spectrum in data_array:
        x, y = (spectrum[:, 0], spectrum[:, 1],)  # separate x- and y-values
        min, max = (y.min(), y.max(),)      # find min and max of y
        y = com.normalize(y, min=min, max=max)   # normalize to min and max of y
        data = np.vstack((x, y,))
        data = data.T
        # data = data.tolist()
        data_array_.append(data)
    data_array_ = np.asarray(data_array_)   # convert new `data_array` to numpy array
    data_array = data_array_        # replace old `data_array` with new one

    # finding peaks
    from scipy.signal import find_peaks_cwt as find_peaks
    from scipy import stats
    import matplotlib.pyplot as plt
    fig = plt.figure(1)
    ax = fig.add_subplot(111)
    # a_sig = 0.01    # to determine whether peak is statistically significant compared to all peaks
    widths = np.arange(1, 10, 1)
    sig_peaks_ind_array = []
    for i, spectrum in enumerate(data_array):
        x, y = (spectrum[:, 0], spectrum[:, 1],)  # separate x- and y-values
        peaks_ind = find_peaks(y, widths)
        snr = stats.signaltonoise(y)
        # determine whether peaks are statistically interesting
        sig_peaks_ind = []  # significant peaks
        for ind in peaks_ind:
            if y[ind] > snr * SNR_FACTOR:
                sig_peaks_ind.append(ind)
        # plotting
        # TODO: Correspond peak dot to spectrum color
        color = (0.0, 0.0, 1/float(i+1),)
        radius = 4
        area = np.pi * radius ** 2  # 0 to 15 point radii
        X = x[sig_peaks_ind]
        Y = y[sig_peaks_ind] + i*PLT_SHIFT
        plt.scatter(X, Y, s=area, c=color, alpha=0.5)
        # ax.annotate('({}, {})'.format(X, Y), xy=(X, Y), textcoords='data')
        sig_peaks_ind_array.append(sig_peaks_ind)

    # data output to file
    peaks_output_path = os.path.join(output_path, PEAKS_OUTPUT_FILENAME)
    with open(peaks_output_path, 'w+') as csv_file:
        writer = csv.writer(csv_file, delimiter='\t')
        for i, _ in enumerate(data_array):
            peaks = data_array[i, sig_peaks_ind_array[i]]
            peaks = peaks.tolist()
            writer.writerows(peaks)
            writer.writerow('\n')

    # plotting
    import matplotlib.pyplot as plt
    plt.figure(1)
    from matplotlib import pylab
    x_dummy, y_dummy = (data_array[0][:,0], data_array[0][:,1],)  # using 0th data set as dummy set
    max_peak = y_dummy.max()
    for i, _ in enumerate(data_array):
        plt.axhline(y=i*PLT_SHIFT, color='k', linestyle='-')    # new axis for each spectrum
        plt.plot(data_array[i][:,0], data_array[i][:,1] + i*PLT_SHIFT, linewidth=0.5)
    # axis labels
    # plt.title('Raman Spectrum for {}'.format(SAMPLE_NAME))
    plt.xlabel('Raman shift [cm$^{-1}$]')
    plt.ylabel('Normalised intensity')
    # remove y-axis values
    frame = pylab.gca()
    frame.axes.get_yaxis().set_ticks([])
    # other
    # plt.legend(LEGEND_KEY)
    plt.tight_layout()
    plt.xlim([x_dummy.min(), x_dummy.max()])
    plt.ylim([0, np.shape(data_array)[0]*PLT_SHIFT + 1])

    # saving plots
    com.saveplot(plt, output_path, "graph.png")
    com.saveplot(plt, output_path, "graph.pdf")
    com.saveplot(plt, output_path, "graph.svg")

    # Plotting peak changes
    import matplotlib.pyplot as plt
    plt.figure(2)
    peaks_array = []
    for i, spectrum in enumerate(data_array):
        peaks = data_array[i, sig_peaks_ind_array[i]]
        peaks = peaks.tolist()
        peaks_array.append(peaks)
    n = len(peaks_array)    # number of files or spectra
    m = com.longest(peaks_array) # number of peaks in dummy file i = 0  # TODO: Define m using the longest number of peaks
    a = np.zeros((m, n, 2,))  # creates np array of size m x n x 2
    # a = [[[0, 0]] * n] * m  # creates list of size m x n x 2
    # a = np.asarray(a)
    for i, spectrum in enumerate(peaks_array):
        for j, peak in enumerate(spectrum):
            a[j, i, 0] = peak[0]
            a[j, i, 1] = peak[1]
        a[j] = np.asarray(a[j])
    f, ax = plt.subplots(2, sharex=True)
    for peak in a:
        x, y = peak[:, 0], peak[:, 1]
        ax[0].plot(x)
        ax[1].plot(y)
    ax[0].set_ylabel("Raman shift [cm$^{-1}$]")
    ax[1].set_ylabel("Intensity")
    ax[1].set_xlabel("Temperature (Index label)")

    plt.show()