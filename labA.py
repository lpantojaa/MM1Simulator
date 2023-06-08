import numpy as np
import math
import heapq
import sys
import matplotlib.pyplot as plt

#Class to abstracty the packet structure
class packet:
    def _init_(self, id, arrival_time, departure_time, size):
        self.id = id
        self.arrival_time = arrival_time
        self.departure_time = departure_time
        self.size = size
    
    def __lt__(self, other):
        return self.arrival_time < other.arrival_time

#Class that generates exponential inter-arrival times and lengths
class poisson_process_source:
    def generate_packet_information(self):
        #Exponential inter-arrival times imply Poisson distributed arrivals
        self.inter_arrival = np.random.exponential(1/self.lambd, 1)
        self.packet_size = math.ceil(np.random.exponential(10000))

#Class that manages the events on the queue using heapq library fro the data structure
class queue:
    def __init__(self):
        self.heap = []

    def insert(self, packet):
        heapq.heappush(self.heap, packet)

    def pop(self):
        if self.heap:
            packet = heapq.heappop(self.heap)
            return packet
        return None

    def is_empty(self):
        return len(self.heap) == 0

class server:
    # 10 Gbits/s = 10000 bits/us
    service_rate = 10000
    total_packets_service_time = 0
    time_in_system = 0
    server_time = 0
    packet_id = 0

    def service(self, queue):
        packet = queue.pop()
        self.packet_id = packet.id
        #Service time is defined by the size of a packet and the defined service rate at the server
        service_time = packet.size / self.service_rate
        self.total_packets_service_time += service_time
        #Update the packet departure time
        packet.departure_time = self.server_time + service_time

        self.time_in_system = packet.departure_time - packet.arrival_time
        #Change the time at the server
        self.server_time = packet.departure_time

class simulator:
    def __init__(self):
        try:
            self.num_of_packets = int(sys.argv[1])
            self.user_lambd = int(sys.argv[2])
        except:
            print("Input must include number_packets and lambda data")
            exit()
        self.system_clock = 0
        self.server_clock = 0
        self.active_queue = queue()
        self.probabilities = [0] * 11
        self.total_packets = 0
        self.length_collection = 0
        self.average_spent_time= 0
    
    def update_probability(self, n):
        if n <= 10:
            self.probabilities[n] += 1
    
    def print_probabilities(self):
        print("Probability that an arriving packet finds n packets in the system:")
        for n, probability in enumerate(self.probabilities):
            p = probability / self.total_packets
            print("P({}) = {}".format(n, p))
    
    def summary(self):
        print("Summary:")
        print("Average number of packets in the system: %d" % (self.length_collection / self.total_packets))
        print("Average time spent by a packet in the system: %.4f us" % (self.average_spent_time))
        
        #Plot probabilities
        x = np.arange(11)
        y = [totals / self.total_packets for totals in self.probabilities]
        plt.plot(x, y)
        plt.xlabel('n')
        plt.ylabel('P(n)')
        plt.title('Probability that an arriving packet finds n packets in the system')
        plt.show()

    def simulate(self):
        current_server= server()
        while self.total_packets < self.num_of_packets:
            source = poisson_process_source()
            source.lambd = self.user_lambd
            source.generate_packet_information()
            
            current_packet = packet()
            current_packet.id = self.total_packets
            current_packet.size = source.packet_size
            current_packet.arrival_time = self.system_clock
            print("time = %4f: pkt %d arrives and finds %d packets in the queue" % (self.system_clock, current_packet.id, len(self.active_queue.heap)))
            
            self.active_queue.insert(current_packet)
            self.length_collection += len(self.active_queue.heap)
            
            #Check if the server has finished its current job
            if self.system_clock >= self.server_clock:
                #If it has, change the server time
                current_server.server_time = self.system_clock
                #Start service for the next job
                current_server.service(self.active_queue)
                #Update the server clock with the departure time of the current job
                self.server_clock = current_server.server_time
                print("time = %f: pkt %d departs after spending %f us in the server" % (self.server_clock, current_server.packet_id, current_server.time_in_system))
            #Bring up the next packet arrival time with the exponentially distributed inter-arrival time
            self.system_clock = self.system_clock + source.inter_arrival
            
            self.update_probability(len(self.active_queue.heap))
            self.total_packets += 1

        while len(self.active_queue.heap) > 0:
            current_server.server_time = self.system_clock
            current_server.service(self.active_queue)
            self.system_clock = current_server.server_time
            print("time = %f: pkt %d departs after spending %f us in the server" % (self.system_clock, current_server.packet_id, current_server.time_in_system))

        self.average_spent_time= current_server.total_packets_service_time / self.num_of_packets    
        self.summary()
        self.print_probabilities()

if __name__ == "__main__":
    simulator = simulator()
    simulator.simulate()