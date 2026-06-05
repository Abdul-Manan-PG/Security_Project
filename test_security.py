import requests
import time
import threading

# Target the local Flask development server
BASE_URL = "http://127.0.0.1:5000"

def print_status(test_name, response, elapsed_time=None):
    """Formats the output for the terminal demo."""
    time_str = f" ({elapsed_time:.2f}s)" if elapsed_time else ""
    print(f"[{test_name}] Status: {response.status_code}{time_str}")

def test_normal_login():
    print("\n--- Initiating Normal Traffic ---")
    response = requests.get(f"{BASE_URL}/login")
    print_status("Normal GET /login", response)

def test_sqli_defense():
    print("\n--- Initiating SQL Injection Simulation ---")
    # Sending a classic SQLi payload that our firewall regex is looking for
    malicious_payload = {
        "email": "admin@system.com",
        "password": "' OR 1=1 --"
    }
    
    response = requests.post(f"{BASE_URL}/login", data=malicious_payload)
    print_status("SQLi POST /login", response)
    if response.status_code == 403:
        print("SUCCESS: Firewall successfully intercepted and dropped the SQLi payload.")

def trigger_tarpit():
    """Sends a rapid burst of requests to trigger the rate-based tarpit."""
    print("\n--- Initiating High-Frequency Traffic (DDoS Simulation) ---")
    
    for i in range(1, 21):
        start_time = time.time()
        # We use a simple GET request to flood the server
        response = requests.get(f"{BASE_URL}/login")
        elapsed_time = time.time() - start_time
        
        print_status(f"Request {i}/20", response, elapsed_time)
        
        # Once the tarpit engages (after 15 requests), you will see the elapsed time jump significantly
        if elapsed_time > 1.0:
            print(">> ALERT: Tarpit latency detected! Server is intentionally delaying the response.")

if __name__ == "__main__":
    print("Starting Information Security Defense Tests...")
    
    # 1. Test normal behavior
    test_normal_login()
    time.sleep(1)
    
    # 2. Test the SQLi Interceptor
    test_sqli_defense()
    time.sleep(1)
    
    # 3. Test the DDoS Tarpit
    trigger_tarpit()
    
    print("\nSimulation complete. Check the SOC Dashboard for the live logs!")