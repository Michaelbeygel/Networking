#!/usr/bin/env python3
import subprocess
import matplotlib.pyplot as plt

def run_external_sim(lam, mu, N, T):
    # Runs your current section1.py script using subprocess
    cmd = ["python3", "section1.py", str(lam), str(mu), str(N), str(T)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Parse the output "A B"
    output = result.stdout.strip().split()
    if len(output) == 2:
        return int(output[0]), int(output[1]) # Returns A and B
    return 0, 0

def experiment_1_4():
    lam = 10.0
    mu = 10.0
    T = 1000.0
    # Increasing N to observe if B vanishes
    N_values = [10, 50, 100, 200, 500, 800, 1000]
    B_results = []

    print(f"Starting experiment: lambda={lam}, mu={mu}, T={T}")
    for n in N_values:
        _, b = run_external_sim(lam, mu, n, T)
        B_results.append(b)
        print(f"For N={n}, dropped/unserviced (B) = {b}")

    # Plotting the results
    plt.figure(figsize=(10, 6))
    plt.plot(N_values, B_results, marker='o', linestyle='-', color='red')
    plt.title(r'Empirical Stability Test: $B$ as a function of $N$ ($\lambda = \mu$)')
    plt.xlabel('System Capacity (N)')
    plt.ylabel('Dropped/Unfinished Requests (B)')
    plt.grid(True, which='both', linestyle='--', alpha=0.5)
    
    # Highlight the lack of convergence
    plt.annotate('B stays high despite larger N', 
                 xy=(N_values[-1], B_results[-1]), 
                 xytext=(N_values[2], B_results[-1] + 50),
                 arrowprops=dict(facecolor='black', shrink=0.05))
    
    plt.show()

if __name__ == "__main__":
    experiment_1_4()