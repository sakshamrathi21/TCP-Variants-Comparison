# Author: Saksham Rathi
# This python script reads the throughput data from the results directory and plots the throughput vs. delay and throughput vs. loss graphs for Reno and Cubic TCP variants.

# Library Imports
import os
import numpy as np
import matplotlib.pyplot as plt
import re

def load_throughput_data(directory, tcp_variant):
    """ Load throughput data from the given directory for the given TCP variant."""
    data = {}
    for file in os.listdir(directory):
        if file.endswith(".txt") and file.startswith(tcp_variant):
            match = re.match(rf'{tcp_variant}_(\d+)ms_(\d+\.\d)%_run\d+\.txt', file)
            if not match:
                # For Loss of 1%
                match = re.match(rf'{tcp_variant}_(\d+)ms_(\d+)%_run\d+\.txt', file)
            if match:
                delay = int(match.group(1))
                loss = float(match.group(2))
                if (delay, loss) not in data:
                    data[(delay, loss)] = []

                with open(os.path.join(directory, file)) as f:
                    for line in f:
                        if "Mbits/sec" in line:
                            throughput_match = re.search(r'([\d.]+) Mbits/sec', line)
                            if throughput_match:
                                data[(delay, loss)].append(float(throughput_match.group(1)))
    return data

def plot_with_error_bars(data, x_values, label, plot_type):
    """ Plot the throughput data with error bars for the given x_values."""
    means = [np.mean(data[key]) if key in data else 0 for key in x_values]
    stds = [np.std(data[key]) if key in data else 0 for key in x_values]
    y_errors = 1.645 * (np.array(stds) / np.sqrt([len(data[key]) if key in data else 1 for key in x_values]))
    x_labels = [str(x[0] if plot_type == 'delay' else x[1]) for x in x_values]
    plt.errorbar(x_labels, means, yerr=y_errors, label=label, marker='o')

delays = [(10, 0.1), (50, 0.1), (100, 0.1)]
losses = [(10, 0.1), (10, 0.5), (10, 1)]

data_reno = load_throughput_data('results', 'reno')
data_cubic = load_throughput_data('results', 'cubic')

for loss in [0.1, 0.5, 1]:
    plt.figure()
    plot_with_error_bars(data_reno, [(d, loss) for d in [10, 50, 100]], 'Reno', 'delay')
    plot_with_error_bars(data_cubic, [(d, loss) for d in [10, 50, 100]], 'Cubic', 'delay')
    plt.xlabel('Delay (ms)')
    plt.ylabel('Throughput (Mbps)')
    plt.title(f'Throughput vs. Delay (Loss={loss}%)')
    plt.legend()
    filename = f'throughput_vs_delay_loss_{loss}.png'
    plt.savefig(filename)
    plt.close()

for delay in [10, 50, 100]:
    plt.figure()
    plot_with_error_bars(data_reno, [(delay, l) for l in [0.1, 0.5, 1]], 'Reno', 'loss')
    plot_with_error_bars(data_cubic, [(delay, l) for l in [0.1, 0.5, 1]], 'Cubic', 'loss')
    plt.xlabel('Loss (%)')
    plt.ylabel('Throughput (Mbps)')
    plt.title(f'Throughput vs. Loss (Delay={delay}ms)')
    plt.legend()
    filename = f'throughput_vs_loss_delay_{delay}ms.png'
    plt.savefig(filename)
    plt.close()
