#!/usr/bin/env python3
import sys
import random
import heapq

class Event:
    def __init__(self, time, type, server_id=None, arrival_time=None):
        self.time = time
        self.type = type  # 0: Arrival to LB, 1: Departure from Server
        self.server_id = server_id
        self.arrival_time = arrival_time # Added to track queue wait

    def __lt__(self, other):
        return self.time < other.time

def run_simulation():
    args = sys.argv[1:]
    if not args: return
    
    T = float(args[0])
    M = int(args[1])
    P = [float(x) for x in args[2:2+M]]
    lam = float(args[2+M])
    Q_sizes = [int(x) for x in args[3+M:3+2*M]]
    mu = [float(x) for x in args[3+2*M:]]

    current_time = 0.0
    event_queue = []
    
    server_busy = [False] * M
    # Change current_queues to store actual arrival times to calculate Tw
    server_waiting_arrivals = [[] for _ in range(M)] 
    
    total_serviced = 0
    total_dropped = 0
    total_wait_time = 0.0
    total_service_time = 0.0
    last_event_time = 0.0

    # First arrival
    first_arrival = random.expovariate(lam)
    if first_arrival <= T:
        heapq.heappush(event_queue, Event(first_arrival, 0))

    while event_queue:
        event = heapq.heappop(event_queue)
        current_time = event.time
        
        if event.type == 0:  # Arrival
            # Schedule next only if before T 
            next_arr = current_time + random.expovariate(lam)
            if next_arr <= T:
                heapq.heappush(event_queue, Event(next_arr, 0))
            
            target = random.choices(range(M), weights=P)[0]
            
            if not server_busy[target]:
                server_busy[target] = True
                s_dur = random.expovariate(mu[target])
                total_service_time += s_dur
                # Tw is 0 here because server was free
                heapq.heappush(event_queue, Event(current_time + s_dur, 1, target))
            elif len(server_waiting_arrivals[target]) < Q_sizes[target]:
                # Add arrival time to queue
                server_waiting_arrivals[target].append(current_time)
            else:
                total_dropped += 1 # Queue full
                
        elif event.type == 1:  # Departure
            total_serviced += 1
            last_event_time = current_time
            s_id = event.server_id
            
            if server_waiting_arrivals[s_id]:
                # Someone is waiting; calculate their Tw 
                arr_time = server_waiting_arrivals[s_id].pop(0)
                total_wait_time += (current_time - arr_time)
                
                s_dur = random.expovariate(mu[s_id])
                total_service_time += s_dur
                heapq.heappush(event_queue, Event(current_time + s_dur, 1, s_id))
            else:
                server_busy[s_id] = False

    avg_tw = total_wait_time / total_serviced if total_serviced > 0 else 0.0
    avg_ts = total_service_time / total_serviced if total_serviced > 0 else 0.0
    
    # Final output rounded to 4 decimal places 
    print(f"{total_serviced} {total_dropped} {last_event_time:.4f} {avg_tw:.4f} {avg_ts:.4f}")

if __name__ == "__main__":
    random.seed() # Ensure different seed per run
    run_simulation()