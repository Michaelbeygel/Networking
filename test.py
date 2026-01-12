#!/usr/bin/env python3
import subprocess

SIM_PATH = "./simulator"

def calculate_theoretical_multi(T, M, P_list, lam, Q_list, mu_list):
    total_expected_A = 0
    total_expected_B = 0
    total_weighted_tw = 0
    total_weighted_ts = 0

    for i in range(M):
        p_i = P_list[i]
        if p_i == 0: continue
        
        lam_i = lam * p_i
        mu_i = mu_list[i]
        N_i = Q_list[i] + 1  # System capacity: Queue + Service
        
        rho = lam_i / mu_i
        
        # Probabilities for M/M/1/N
        if abs(rho - 1.0) < 1e-7:
            p_loss = 1 / (N_i + 1)
            L = N_i / 2
        else:
            p_loss = ((1 - rho) * (rho**N_i)) / (1 - rho**(N_i + 1))
            L = (rho / (1 - rho)) - ((N_i + 1) * (rho**(N_i + 1))) / (1 - rho**(N_i + 1))
        
        p0 = (1 - rho) / (1 - rho**(N_i + 1)) if abs(rho - 1.0) > 1e-7 else 1 / (N_i + 1)
        Lq = L - (1 - p0)
        lam_eff = lam_i * (1 - p_loss)
        
        # Stats for this server
        A_i = lam_eff * T
        B_i = (lam_i * p_loss) * T
        Tw_i = Lq / lam_eff if lam_eff > 0 else 0
        Ts_i = 1 / mu_i
        
        total_expected_A += A_i
        total_expected_B += B_i
        total_weighted_tw += (Tw_i * A_i)
        total_weighted_ts += (Ts_i * A_i)

    # Global Averages
    final_A = total_expected_A
    final_B = total_expected_B
    final_tw = total_weighted_tw / total_expected_A if total_expected_A > 0 else 0
    final_ts = total_weighted_ts / total_expected_A if total_expected_A > 0 else 0
    
    return final_A, final_B, T, final_tw, final_ts

def check_margin(name, actual, theoretical):
    # If the theoretical value is 0, we allow a small absolute error (epsilon)
    # instead of a percentage, as 10% of 0 is always 0.
    if abs(theoretical) < 1e-7:
        # For B (dropped), we allow a small amount of random noise
        # For Tw (wait time), it must be virtually zero
        if name == "B":
            is_ok = actual < 100 # Allow some noise for dropped requests in stable systems
        else:
            is_ok = abs(actual) < 1e-4 
    else:
        # Standard 10% margin check 
        lower = theoretical * 0.9
        upper = theoretical * 1.1
        is_ok = lower <= actual <= upper
    
    status = "PASS" if is_ok else "FAIL"
    print(f"  {name:<5}: Act={actual:>10.4f} | Th={theoretical:>10.4f} | {status}")
    return is_ok

def run_test(desc, params):
    print(f"\n--- {desc} ---")
    T = float(params[0])
    M = int(params[1])
    P = [float(x) for x in params[2:2+M]]
    lam = float(params[2+M])
    Q = [int(x) for x in params[3+M:3+2*M]]
    mu = [float(x) for x in params[3+2*M:]]
    
    th_A, th_B, th_Tend, th_Tw, th_Ts = calculate_theoretical_multi(T, M, P, lam, Q, mu)

    try:
        proc = subprocess.run([SIM_PATH] + params, capture_output=True, text=True, timeout=120)
        output = proc.stdout.strip().split()
        if len(output) != 5:
            print(f"  Error: Expected 5 values, got: {output}")
            return
        
        act = [float(x) for x in output]
        results = [
            check_margin("A", act[0], th_A),
            check_margin("B", act[1], th_B),
            check_margin("Tend", act[2], th_Tend),
            check_margin("Tw", act[3], th_Tw),
            check_margin("Ts", act[4], th_Ts)
        ]
        print(">> RESULT: " + ("PASSED" if all(results) else "FAILED"))
    except Exception as e:
        print(f"  Error running simulator: {e}")

if __name__ == "__main__":
    tests = [
        ("5.2.1.1: Single Server Stable", ["5000", "1", "1", "20", "1000", "40"]),
        ("5.2.1.2: Multi-Server Single Target", ["5000", "4", "1", "0", "0", "0", "20", "1000", "1000", "1000", "1000", "40", "40", "40", "40"]),
        ("5.2.1.5: Zero Queue (M/M/1/1)", ["5000", "4", "0.25", "0.25", "0.25", "0.25", "20", "0", "0", "0", "0", "40", "40", "40", "40"]),
        ("5.2.1.6: Low Service Rate (Unstable)", ["5000", "4", "0.25", "0.25", "0.25", "0.25", "20", "100", "100", "100", "100", "0.5", "0.5", "0.5", "0.5"]),
    ]
    for desc, p in tests:
        run_test(desc, p)