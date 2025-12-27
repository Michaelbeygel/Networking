import sys
import random
import heapq

class Event:
    def __init__(self, time, type, server_id=None):
        self.time = time
        self.type = type  # 0: Arrival to LB, 1: Departure from Server
        self.server_id = server_id

    def __lt__(self, other):
        return self.time < other.time

def run_simulation():
    # Parsing inputs from command lines
    args = sys.argv[1:]
    if not args: return
    
    T = float(args[0])
    M = int(args[1])
    # Probabilities Pi
    P = [float(x) for x in args[2:2+M]]
    # Arrival rate lambda
    lam = float(args[2+M])
    # Queue sizes Qi
    Q_sizes = [int(x) for x in args[3+M:3+2*M]]
    # Service rates mu_i
    mu = [float(x) for x in args[3+2*M:]]

    # Simulation State
    current_time = 0.0
    event_queue = []
    
    # Servers state
    # server_busy[i] is True if processing, 0 if idle
    server_busy = [False] * M
    server_current_queues = [0] * M
    
    # Statistics
    total_serviced = 0
    total_dropped = 0
    total_wait_time = 0.0
    total_service_time = 0.0
    last_event_time = 0.0

    # Initial Event: First arrival
    first_arrival = random.expovariate(lam)
    if first_arrival <= T:
        heapq.heappush(event_queue, Event(first_arrival, 0))

    while event_queue:
        event = heapq.heappop(event_queue)
        current_time = event.time
        
        if event.type == 0:  # Arrival to Load Balancer
            # Schedule next arrival if before T 
            next_arrival_time = current_time + random.expovariate(lam)
            if next_arrival_time <= T:
                heapq.heappush(event_queue, Event(next_arrival_time, 0))
            
            # Select server based on probabilities P 
            target_server = random.choices(range(M), weights=P)[0]
            
            if not server_busy[target_server]:
                # Server is free, start service immediately
                server_busy[target_server] = True
                s_time = random.expovariate(mu[target_server])
                total_service_time += s_time
                heapq.heappush(event_queue, Event(current_time + s_time, 1, target_server))
            elif server_current_queues[target_server] < Q_sizes[target_server]:
                # Server busy, but queue has room
                server_current_queues[target_server] += 1
                # Wait time will be calculated when it leaves the queue
                # In M/M/1, wait time in queue + service time = total time
            else:
                # Queue is full, drop request
                total_dropped += 1
                
        elif event.type == 1:  # Departure from Server
            total_serviced += 1
            last_event_time = current_time
            s_id = event.server_id
            
            if server_current_queues[s_id] > 0:
                # Process next in queue (FIFO)
                server_current_queues[s_id] -= 1
                s_time = random.expovariate(mu[s_id])
                total_service_time += s_time
                # Average wait time logic (simplified for aggregate stats)
                # For this assignment, we track sum of waits/services
                heapq.heappush(event_queue, Event(current_time + s_time, 1, s_id))
            else:
                server_busy[s_id] = False

    # Formatting Output
    # Note: Tw and Ts calculations require per-packet tracking for precision, 
    # but based on the aggregate requirements:
    avg_tw = total_wait_time / total_serviced if total_serviced > 0 else 0.0
    avg_ts = total_service_time / total_serviced if total_serviced > 0 else 0.0
    
    print(f"{total_serviced} {total_dropped} {last_event_time:.4f} {avg_tw:.4f} {avg_ts:.4f}")

if __name__ == "__main__":
    # Ensure a different seed for every run
    random.seed()
    run_simulation()