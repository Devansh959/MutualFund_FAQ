import requests
import threading
import time

API_URL = "http://localhost:8000/ask"

def send_query(thread_id, query):
    print(f"[{thread_id}] Sending: {query}")
    try:
        response = requests.post(
            API_URL,
            json={"query": query, "thread_id": thread_id}
        )
        if response.status_code == 200:
            print(f"[{thread_id}] Received: {response.json()['answer'][:50]}...")
        else:
            print(f"[{thread_id}] Error: {response.status_code}")
    except Exception as e:
        print(f"[{thread_id}] Connection Error: {e}")

# Test 1: Concurrency (Simultaneous requests)
print("--- Starting Concurrency Test ---")
threads = []
for i in range(5):
    t = threading.Thread(target=send_query, args=(f"thread_{i}", "What is the exit load for HDFC Mid Cap Fund?"))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

# Test 2: Isolation (Check if history from one leaks to another)
print("\n--- Starting Isolation Test ---")
# 1. Ask something in Thread A
send_query("thread_A", "Remember this secret code: BANANA-123. What is it?")
# 2. Ask something in Thread B
send_query("thread_B", "What was the secret code I just told you?")
# 3. Check Thread A again
send_query("thread_A", "What was that secret code?")

print("\nVerification Complete. If Thread B says it doesn't know the code, isolation is working.")
