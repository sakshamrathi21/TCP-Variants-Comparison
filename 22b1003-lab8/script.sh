#!/bin/bash # Script will be run using bash

# Author: Saksham Rathi
# The script runs a series of iperf experiments to test the performance of different TCP congestion control algorithms under varying network conditions. Descriptive variable names along with detailed comments are used to explain the script.

FILE_SIZE=20 # The size of the file (in megabytes) to be used in the iperf tests
BANDWIDTH="100mbit" # Bandwidth rate limit
MTU=1500    # Maximu Transmission Unit size for packets
EXPERIMENT_RUNS=20 # Number of times to run each experiment
TCP_VARIANTS=("reno" "cubic") # TCP congestion control algorithms to test
DELAYS=("10ms" "50ms" "100ms") # Network delay values to test
LOSSES=("0.1%" "0.5%" "1%") # Network packet loss values to test
OUTPUT_DIR="results" # Directory to store the output files

# Setup MTU on the loopback interface
sudo ifconfig lo mtu $MTU

# Create output directory if it doesn't exist
mkdir -p $OUTPUT_DIR

for tcp_variant in "${TCP_VARIANTS[@]}"; do
    sudo sysctl -w net.ipv4.tcp_congestion_control=$tcp_variant # Sets the TCP congestion control algorithm

    for delay in "${DELAYS[@]}"; do
        for loss in "${LOSSES[@]}"; do
            # Apply network settings
            sudo tc qdisc del dev lo root 2> /dev/null # Deletes any existing traffic control settings on the loopback interface
            sudo tc qdisc add dev lo root handle 1: tbf rate $BANDWIDTH burst 32kbit latency 50ms # Adds a Token Bucket Filter (TBF) queueing discipline to the loopback interface
            sudo tc qdisc add dev lo parent 1:1 netem delay $delay loss $loss # Adds a NetEm qdisc to stimulate network delay and packet loss


            for run in $(seq 1 $EXPERIMENT_RUNS); do
                iperf -s -p 5001 -D  # Starts iperf server in the background
                sleep 1 # Pauses for 1 second to allow the server to start
                iperf -c 127.0.0.1 -p 5001 -n "$FILE_SIZE"M > "$OUTPUT_DIR/${tcp_variant}_${delay}_${loss}_run${run}.txt" # Runs the iperf client to send data and logs the output to a file

                ss -tni | grep 'tcp' >> "$OUTPUT_DIR/${tcp_variant}_ss_output.txt" # Captures TCP socket statistics and appends them to a file.

               	wait # Waits for the iperf server to finish
		        pkill -f "iperf" # Kills the iperf server
		        sleep 1 # Pauses for 1 second before the next run
            done
        done
    done
done


sudo tc qdisc del dev lo root # Removes any traffic control settings on the loopback interface.
