import numpy as np
import common as com

def get_curve(path):
    if path is not None:  # if input path provided
        curve = read_curve_from_file(path)
    else:
        curve = read_curve_from_usr()     # read curve from user input in console
    return curve

def read_curve_from_usr():
    import numpy as np
    i = 0
    curve = []
    while True:
        rate = input("Please provide rate, rate({}): ".format(i))
        if rate.lower() == "exit":
            break
        T = input("Please provide T, T({}): ".format(i))
        if T.lower() == "exit":
            break
        wait = input("Please provide wait time, wait({}): ".format(i))
        if wait.lower() == "exit":
            break
            
        # valid = False
        # while not valid:
        #     rate = input("Please provide rate, rate({}): ".format(i))
        #     if isinstance(rate, float):
        #         valid = True
        #     elif rate == "exit":
        #         valid = True
        # if rate.lower() == "exit":
        #     break
        # 
        # valid = False
        # while not valid:
        #     T = input("Please provide temperature, T({}): ".format(i))
        #     if isinstance(T, float):
        #         valid = True
        #     elif T == "exit":
        #         valid = True
        # if T.lower() == "exit":
        #     break
        # 
        # valid = False
        # while not valid:
        #     wait = input("Please provide wait time, t({}): ".format(i))
        #     if isinstance(wait, float):
        #         valid = True
        #     elif wait == "exit":
        #         valid = True
        # if wait.lower() == "exit":
        #     break

        rate = float(rate)
        T = float(T)
        wait = float(wait)

        curve.append([i, rate, T, wait])

        i = i + 1
    curve = np.asarray(curve)
    return curve

def read_curve_from_file(file):
    import csv
    curve = []
    with open(file, 'r') as fh:
        open_file = csv.reader(fh, delimiter='\t')
        for line in open_file:
            line_ = []
            for l in line:
                l = float(l)
                line_.append(l)
            curve.append(line_)
    return curve

def get_curve_points(curve):
    # initial values
    T = curve[0][1]
    t = 0.0
    arr = [[t, T]]
    maxlen = len(curve)
    # calculation
    for i, _ in enumerate(curve):
        i = i + 1
        if i == maxlen:
            break

        T0 = T
        t0 = t
        T = curve[i][1]
        rate = curve[i][0]
        dT = T - T0

        t = t0 + abs(dT) / rate

        arr.append([t, T])

        # add wait time
        wait = curve[i][2]  # in minutes
        t = t + wait
        arr.append([t, T])

    return arr

def find_max_img_num(time, imgdt, t0 = 0.0):
    maxtime = max(time)
    maxint = ( maxtime - t0 ) / imgdt
    maxint = int(maxint)
    print("Max image number is {}.".format(maxint))

    return maxint

def interp_points(arr):
    from scipy.interpolate import interp1d
    arr = np.array(arr)
    x, y = arr[:, 0], arr[:, 1]
    f = interp1d(x, y)
    return f

def get_temp_from_funct(T, imgdt, imgidx=None, t0=0.0):
    if imgidx is None:
        while True:
            imgidx = input("Which image number would you like know the temperature of? [integer]: ")
            if imgidx == 'exit':
                return
            try:
                imgidx = int(imgidx)
            except ValueError:
                print("Please provide an integer!")
                continue
            ti = t0 + imgidx * imgdt
            print("Temperature of image {} is {}'C.".format(imgidx, T(ti)))
    else:
        ti = t0 + imgidx * imgdt
        Ti = T(ti)
        return Ti

def get_temp(arr, imgdt, imgidx=None, t0=0.0):
    Tf = interp_points(arr)
    find_max_img_num(arr[:, 0], imgdt, t0=t0)
    get_temp_from_funct(Tf, imgdt, imgidx=imgidx, t0=t0)

if __name__ == '__main__':

    com.print_running_message(__file__)

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', action='store', dest='input', help='input file')

    args = parser.parse_args()
    input_path = args.input
    curve = get_curve(input_path)

    plot_array = get_curve_points(curve)

    # get times
    imgdt = 60.0
    if imgdt is None:
        imgdt = input("What is the time between each image capture? [float, in seconds]: ")
    imgdt = float(imgdt)
    imgdt = imgdt / 60.0 # in minutes
    imgfreq = 1.0 / imgdt  # in images/minute

    # imgnums = input("What is the total number of image captures? [integer, dimensionless]: ")
    # imgnums = int(imgnums)

    plot_array = np.array(plot_array)
    x, y = plot_array[:, 0], plot_array[:, 1]

    import matplotlib.pyplot as plt
    plt.plot(x, y)
    imgt = 0.0
    maxtime = max(x)
    while True:
        imgt = imgt + imgdt
        if imgt > maxtime:
            break
        plt.axvline(imgt, linewidth=0.5, c='gray')

    plt.title("Temperature Curve")
    plt.ylabel("Temperature $T$ [$\degree$C]")
    plt.xlabel("Time $t$ [minutes]")

    plt.show()

    get_temp(plot_array, imgdt=imgdt)


