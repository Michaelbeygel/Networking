#!/usr/bin/env python3
import sys
import random
import heapq

class Event:
    def __init__(self, time, event_type):
        self.time = time
        self.type = event_type  # 0: Arrival, 1: Departure

    def __lt__(self, other):
        return self.time < other.time

def run_simulation():

    # Expected args: lambda, mu, N, T
    if len(sys.argv) != 5:
        print("Usage: ./section1.py <lambda> <mu> <N> <T>")
        return

    lam = float(sys.argv[1])  # Arrival rate
    mu = float(sys.argv[2])   # Service rate
    N = int(sys.argv[3])      # System capacity (Queue + Service)
    T = float(sys.argv[4])    # Simulation time

    # State variables
    current_time = 0.0
    events = []
    
    # N includes the request in service
    # We track the number of requests currently in the system
    requests_in_system = 0
    
    # Statistics
    total_arrivals = 0   # Needed to calculate B
    total_serviced = 0   # Metric A
    
    # Initialize random seed (ensure difference every run)
    random.seed()

    # Schedule first arrival
    first_arrival_time = random.expovariate(lam)
    if first_arrival_time <= T:
        heapq.heappush(events, Event(first_arrival_time, 0))

    # Event Loop
    while events:
        event = heapq.heappop(events)
        
        # Stop simulation at time T
        if event.time > T:
            break
            
        current_time = event.time
        
        if event.type == 0:  # ARRIVAL
            total_arrivals += 1
            
            # 1. Schedule next arrival
            next_arrival = current_time + random.expovariate(lam)
            if next_arrival <= T:
                heapq.heappush(events, Event(next_arrival, 0))
            
            # 2. Handle Logic
            if requests_in_system < N:
                # If server is free (system was empty), start service immediately
                if requests_in_system == 0:
                    service_time = random.expovariate(mu)
                    # Check if service ends before T? 
                    # The spec implies we schedule it, but if it ends > T it won't count as served.
                    heapq.heappush(events, Event(current_time + service_time, 1))
                
                requests_in_system += 1
            else:
                # Dropped due to full queue. 
                # We simply don't increment requests_in_system.
                # B counts these later.
                pass

        elif event.type == 1:  # DEPARTURE
            total_serviced += 1
            requests_in_system -= 1
            
            # If there are still requests waiting, schedule next service
            if requests_in_system > 0:
                service_time = random.expovariate(mu)
                heapq.heappush(events, Event(current_time + service_time, 1))

    # 1.2. Output Calculation
    # B: Requests not served due to full queue OR end of time
    # This is effectively Total Arrivals - Total Successfully Serviced.
    total_dropped = total_arrivals - total_serviced
    
    # Output: A B
    print(f"{total_serviced} {total_dropped}")

if __name__ == "__main__":
    run_simulation()