import requests

# IP adresa Shelly smart plug
PLUG_IP = 'http://10.42.0.222'

# Funkcia na zapnutie Shelly smart plug
def turn_on():
    response = requests.post(f'{PLUG_IP}/relay/0/on')
    if response.status_code == 200:
        print("Smart plug is now ON.")
    else:
        print(f"Failed to turn on. Status code: {response.status_code}")

# Funkcia na vypnutie Shelly smart plug
def turn_off():
    response = requests.post(f'{PLUG_IP}/relay/0/off')
    if response.status_code == 200:
        print("Smart plug is now OFF.")
    else:
        print(f"Failed to turn off. Status code: {response.status_code}")

# Funkcia na zistenie stavu Shelly smart plug
def get_status():
    response = requests.get(f'{PLUG_IP}/relay/0')
    if response.status_code == 200:
        data = response.json()
        if data['relay']['0']['state'] == 'on':
            print("Smart plug is ON.")
        else:
            print("Smart plug is OFF.")
    else:
        print(f"Failed to get status. Status code: {response.status_code}")

# Hlavná funkcia, ktorá umožní užívateľovi vybrať akciu
def main():
    print("Shelly Smart Plug Control")
    print("1. Turn On")
    print("2. Turn Off")
    print("3. Get Status")
    choice = input("Enter your choice: ")

    if choice == '1':
        turn_on()
    elif choice == '2':
        turn_off()
    elif choice == '3':
        get_status()
    else:
        print("Invalid choice!")

# Spustenie hlavnej funkcie
if __name__ == '__main__':
    main()
