#Class to abstracty the packet structure
class packet:
    def _init_(self, id, arrival_time, departure_time, size):
        self.id = id
        self.arrival_time = arrival_time
        self.departure_time = departure_time
        self.size = size
    
    def __lt__(self, other):
        return self.arrival_time < other.arrival_time