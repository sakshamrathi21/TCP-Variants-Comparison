# TCP-Variants-Comparison

## How to run the script

```bash
./script.sh
```
(Execution permissions already provided)

This script will compare the bandwidth for iperf server and client across TCP Reno and TCP Cubic for various delay and loss values (20 runs each). All the bandwidth values will be stored as .txt files in the "results" directory.

## How to generate the plots
```bash
python3 analyze_data.py
```

Assuming that the results are already generated, this python script will generate the corresponding plots.

## Wireshark Results
First run ```sudo wireshark``` on terminal and capture packets for lo interface
```bash
sudo sysctl -w net.ipv4.tcp_congestion_control="reno"
sudo tc qdisc add dev lo root netem delay 10ms loss 0.1%
iperf -s -p 5001 -D
iperf -c 127.0.0.1 -p 5001 -t 5
```
We will have to do this for different delay and loss values and also for TCP cubic. pcapng files for 4 runs have also been added along with the window scaling plots.
