#!/usr/bin/env python3
import sys
import random
import heapq

class Event:
    def __init__(self, time, type, server_id=None, arrival_time=None):
        self.time = time
        self.type = type  # 0: Arrival, 1: Departure
        self.server_id = server_id
        self.arrival_time = arrival_time 

    # Needed for the priority queue to sort events by time
    def __lt__(self, other):
        return self.time < other.time

def run_simulation():
    args = sys.argv[1:]
    if not args: return
    
    # Input parameters parsing
    T = float(args[0])
    M = int(args[1])
    P = [float(x) for x in args[2:2+M]]
    lam = float(args[2+M])
    Q_sizes = [int(x) for x in args[3+M:3+2*M]]
    mu = [float(x) for x in args[3+2*M:]]

    current_time = 0.0
    event_queue = [] 
    
    server_busy = [False] * M
    # Holds arrival times of requests waiting in the queue for each server
    server_waiting_arrivals = [[] for _ in range(M)] 
    
    total_serviced = 0
    total_dropped = 0
    total_wait_time = 0.0
    total_service_time = 0.0
    last_event_time = 0.0

    # First arrival trigger
    first_arrival = random.expovariate(lam)
    if first_arrival <= T:
        heapq.heappush(event_queue, Event(first_arrival, 0))

    while event_queue:
        event = heapq.heappop(event_queue)
        current_time = event.time
        
        if event.type == 0:  # Arrival logic
            # Schedule next arrival only if we haven't reached time T
            next_arr = current_time + random.expovariate(lam)
            if next_arr <= T:
                heapq.heappush(event_queue, Event(next_arr, 0))
            
            # Select server based on probabilities Pi
            target = random.choices(range(M), weights=P)[0]
            
            if not server_busy[target]:
                server_busy[target] = True
                s_dur = random.expovariate(mu[target])
                total_service_time += s_dur
                # Start service immediately (Wait time = 0)
                heapq.heappush(event_queue, Event(current_time + s_dur, 1, target, current_time))
            elif len(server_waiting_arrivals[target]) < Q_sizes[target]:
                # Add to queue if there is space
                server_waiting_arrivals[target].append(current_time)
            else:
                total_dropped += 1
                
        elif event.type == 1:  # Departure logic
            total_serviced += 1
            last_event_time = current_time
            s_id = event.server_id
            
            if server_waiting_arrivals[s_id]:
                # Pull next from queue (FIFO) and calculate how long it waited
                arr_time = server_waiting_arrivals[s_id].pop(0)
                total_wait_time += (current_time - arr_time)
                
                s_dur = random.expovariate(mu[s_id])
                total_service_time += s_dur
                heapq.heappush(event_queue, Event(current_time + s_dur, 1, s_id, arr_time))
            else:
                server_busy[s_id] = False

    # Output calculation
    avg_tw = total_wait_time / total_serviced if total_serviced > 0 else 0.0
    avg_ts = total_service_time / total_serviced if total_serviced > 0 else 0.0
    
    print(f"{total_serviced} {total_dropped} {last_event_time:.4f} {avg_tw:.4f} {avg_ts:.4f}")

if __name__ == "__main__":
    random.seed() 
    run_simulation()