#!/usr/bin/env python3
import sys
import random
import heapq

# Helper class to store event details
class Event:
    def __init__(self, time, type, arrival_time=None):
        self.time = time
        self.type = type  # 0: Arrival, 1: Departure
        self.arrival_time = arrival_time # When did this request enter the system?

    def __lt__(self, other):
        return self.time < other.time

def run_simulation():
    if len(sys.argv) != 5:
        print("Usage: ./section2.py <lambda> <mu> <N> <T>")
        return

    lam = float(sys.argv[1])
    mu = float(sys.argv[2])
    N = int(sys.argv[3])
    T = float(sys.argv[4])

    current_time = 0.0
    events = []
    
    # Store arrival times of requests currently in the queue/service
    # This list acts as our FIFO queue buffer
    waiting_queue = [] 
    
    total_serviced = 0
    total_wait_time_sum = 0.0
    
    random.seed() # Different seed every run

    # Schedule first arrival
    first_arrival = random.expovariate(lam)
    if first_arrival <= T:
        heapq.heappush(events, Event(first_arrival, 0))

    while events:
        event = heapq.heappop(events)
        
        # Strictly stop processing new events after T
        # (Though we still need to account for queue state if calculating B, 
        # but Section 2 only asks for Served and Wait Time)
        if event.time > T:
            break
            
        current_time = event.time
        
        if event.type == 0:  # ARRIVAL
            # 1. Schedule next arrival
            next_arr = current_time + random.expovariate(lam)
            if next_arr <= T:
                heapq.heappush(events, Event(next_arr, 0))
            
            # 2. Logic
            if len(waiting_queue) < N:
                # If server is free (queue was empty), schedule departure immediately
                if len(waiting_queue) == 0:
                    service_time = random.expovariate(mu)
                    heapq.heappush(events, Event(current_time + service_time, 1))
                
                # Add this request's arrival time to the queue
                waiting_queue.append(current_time)

        elif event.type == 1:  # DEPARTURE
            total_serviced += 1
            
            # Pop the request that just finished (FIFO = pop index 0)
            arrival_time = waiting_queue.pop(0)
            
            # Calculate how long it was in the system (Wait + Service)
            time_in_system = current_time - arrival_time
            total_wait_time_sum += time_in_system
            
            # If there are still people waiting, schedule the NEXT departure
            if len(waiting_queue) > 0:
                service_time = random.expovariate(mu)
                heapq.heappush(events, Event(current_time + service_time, 1))

    # Calculate Average
    avg_wait = total_wait_time_sum / total_serviced if total_serviced > 0 else 0.0
    
    # Output: Served Requests, Average Wait Time
    print(f"{total_serviced} {avg_wait:.4f}")

if __name__ == "__main__":
    run_simulation()