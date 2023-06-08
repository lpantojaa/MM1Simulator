# MM1Simulator

Laboratory 1 for TELE4642 course - a simulator for a M/M/1 Queue System.

This simulator demonstrates two different scenarios. In both scenarios, the simulator models the behavior of a single server queueing system, tracking various metrics including average queue lengths and average time spent in the system by a packet.

## Part A

Part A generates packets with exponentially distributed sizes and inter-arrival times, implying Poisson arrivals. The rate of packet arrivals and the number of packets to generate are specified as command-line arguments at the start of the simulation.

Usage: `python labA.py [num_of_packets] [packet_arrival_rate]`

Example: `python labA.py 10000 1.8`

## Part B

Part B differs from Part A by reading packet arrivals from a trace file of real Internet traffic and schedules appropriate events. The first trace file represents a traffic with an average service rate of 4Gbps and contains two columns: the first column represents the inter-arrival time in microseconds(us) and the second column represents the packet size in Bytes. The second one has an avergade service rate of 7Gbps.

Usage: `python labB.py [trace_file] [service_rate]`

Example: `python labB.py trace1.txt 4000`

## Dependencies

This project requires the following Python libraries:

- numpy
- math
- heapq
- argparse
- matplotlib

## Installing Dependencies

You can install these dependencies using pip, a package manager for Python. If you have pip installed, you can run the following commands in your terminal:

```bash
pip install numpy
pip install matplotlib
