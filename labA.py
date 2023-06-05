import numpy as np
import math
import heapq

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