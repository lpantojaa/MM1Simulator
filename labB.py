import numpy as np
import math
import heapq
import argparse
import matplotlib.pyplot as plt
import csv

#Class to import the file
class TraceFileSource:
    def __init__(self, file_name):
        self.file_name = file_name
        self.packet_data = self.process_file()

    def process_file(self):
        # Open file and read data
        with open(self.file_name, 'r') as file:
            data = []
            for line in file.readlines():
                # Split each line into inter-arrival time and packet size
                inter_arrival_time, packet_size = map(float, line.strip().split())
                # Convert packet size from bytes to bits
                packet_size = packet_size * 8
                data.append((inter_arrival_time, packet_size))
            #Make the data iterable
            return iter(data)

    def generate_packet_information(self):
        try:
            return next(self.packet_data)
        except StopIteration:
            return None, None

#Class to abstract the packet structure
class Packet:
    def __init__(self, id, arrival_time, size):
        self.id = id
        self.arrival_time = arrival_time
        self.departure_time = None
        self.size = size
    
    def __lt__(self, other):
        return self.arrival_time < other.arrival_time

#Class that manages the events on the queue using heapq library fro the data structure
class Queue:
    def __init__(self):
        self.heap = []

    def insert(self, packet):
        heapq.heappush(self.heap, packet)

    def pop(self):
        if self.is_empty():
            raise Exception("Queue is empty, can't pop a packet.")
        return heapq.heappop(self.heap)

    def is_empty(self):
        return len(self.heap) == 0

class Server:
    time_in_system = 0
    server_time = 0
    current_packet_id = 0
    
    def __init__(self, service_rate):
        self.service_rate = service_rate

    def service(self, queue):
        packet = queue.pop()
        self.current_packet_id = packet.id
        #Service time is defined by the size of a packet and the defined service rate at the server
        service_time = packet.size / self.service_rate
        #Update the packet departure time
        packet.departure_time = self.server_time + service_time

        self.time_in_system = packet.departure_time - packet.arrival_time
        #Change the time at the server
        self.server_time = packet.departure_time

class Simulator:
    def __init__(self, trace_file, service_rate):
        self.system_clock = 0
        self.server_clock = 0
        self.active_queue = Queue()
        self.probabilities = [0] * 11
        self.total_packets = 0
        self.total_queue_lengths = 0
        self.total_time_in_system = 0
        self.trace_file = trace_file
        self.service_rate = service_rate
    
    def update_probability(self, n):
        if n <= 10:
            self.probabilities[n] += 1
    
    def print_probabilities(self):
        print("Probability that an arriving packet finds n packets in the system:")
        for n, probability in enumerate(self.probabilities):
            p = probability / self.total_packets
            print("P({}) = {}".format(n, p))
    
    def summary(self):
        average_queue_length = self.total_queue_lengths / self.total_packets
        average_time_in_system = self.total_time_in_system / self.total_packets
        print("Summary:")
        print("Average number of packets in the system: %d" % (average_queue_length))
        print("Average time spent by a packet in the system: %.4f us" % (average_time_in_system))
        self.print_probabilities()
        
        #Plot probabilities
        plt.style.use('ggplot')
        x = np.arange(11)
        y = [totals / self.total_packets for totals in self.probabilities]

        #Adjust size of the figure
        plt.figure(figsize=(10, 6))
        #Add marker and increase line width
        plt.plot(x, y, marker='o', linewidth=2, color="blue") 

        plt.xlabel('Number of Packets in System (n)', fontsize=14)
        plt.ylabel('Probability (P)', fontsize=14)
        plt.title('Probability of an Arriving Packet Finding n Packets in System', fontsize=16)

        plt.grid(True)
        #Show every x value in plot
        plt.xticks(x)
        plt.show()

    def simulate(self):
        current_server = Server(self.service_rate)
        source = PoissonProcessSource(self.packet_arrival_rate)
        while self.total_packets < self.num_of_packets:
            inter_arrival, packet_size = source.generate_packet_information() 
            current_packet = Packet(self.total_packets, self.system_clock, packet_size)

            print("[%.4f us]: pkt %d arrives and finds %d packets in the queue" % (self.system_clock, current_packet.id, len(self.active_queue.heap)))
            
            self.active_queue.insert(current_packet)
            self.total_queue_lengths += len(self.active_queue.heap)
            
            #Check if the server has finished its current job
            if self.system_clock >= self.server_clock:
                #If it has, change the server time
                current_server.server_time = self.system_clock
                #Start service for the next job
                current_server.service(self.active_queue)
                #Acummulate total time in system
                self.total_time_in_system += current_server.time_in_system   
                #Update the server clock with the departure time of the current job
                self.server_clock = current_server.server_time
                print("[%.4f us]: pkt %d departs after spending %.4f us in the server" % (self.server_clock, current_server.current_packet_id, current_server.time_in_system))

            #Bring up the next packet arrival time with the exponentially distributed inter-arrival time
            self.system_clock = self.system_clock + inter_arrival
            
            self.update_probability(len(self.active_queue.heap))
            self.total_packets += 1

        while not self.active_queue.is_empty():
            current_server.server_time = self.system_clock
            current_server.service(self.active_queue)
            #Acummulate total time in system
            self.total_time_in_system += current_server.time_in_system
            #No server_clock is needed as no new packets are being received
            self.system_clock = current_server.server_time
            print("[%.4f us]: pkt %d departs after spending %.4f us in the server" % (self.system_clock, current_server.current_packet_id, current_server.time_in_system))

        self.summary()

def parse_arguments():
    parser = argparse.ArgumentParser(description='Simulate a packet server system with a trace file and a custom service rate.')
    parser.add_argument('trace_file', type=str, help='Path to the trace file')
    parser.add_argument('service_rate', type=int, help='Service rate in bits/us')

    args = parser.parse_args()

    if args.service_rate <= 0:
        raise argparse.ArgumentTypeError("service_rate should be greater than 0")

    return args.trace_file, args.service_rate

def main():
    trace_file, service_rate = parse_arguments()
    simulator = Simulator(trace_file, service_rate)
    simulator.simulate()

if __name__ == "__main__":
    main()