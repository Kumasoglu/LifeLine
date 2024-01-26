import network
import urequest

class WiFiConnection:
    def __init__(self, ssid, password, attempts=2, timeout=10):
        self.ssid = ssid
        self.password = password
        self.attempts = attempts  # Number of attempts to connect
        self.timeout = timeout  # Timeout for each Wi-Fi connection attempt
        self.wlan = network.WLAN(network.STA_IF)

    def connect(self):
        self.wlan.active(True)
        for attempt in range(self.attempts):
            print(f"Attempting to connect to Wi-Fi (Attempt {attempt + 1} of {self.attempts})")
            self.wlan.connect(self.ssid, self.password)

            start_time = time.ticks_ms()
            while not self.wlan.isconnected():
                if time.ticks_diff(time.ticks_ms(), start_time) > self.timeout * 1000:
                    break  # Exit the while loop if timeout is reached
                time.sleep(1)

            if self.wlan.isconnected():
                print("Connected to Wi-Fi")
                return True

            # Disconnect before next attempt
            self.wlan.disconnect()

        print("Failed to connect to Wi-Fi after multiple attempts")
        return False

class OTAUpdater:
    def __init__(self, base_url, file_list):
        self.base_url = base_url
        self.file_list = file_list

    def update(self):
        for file in self.file_list:
            url = f"{self.base_url}/{file}"
            response = urequests.get(url)
            if response.status_code == 200:
                with open(file, 'w') as f:
                    f.write(response.text)
                print(f"Updated {file}")
            else:
                print(f"Failed to download {file}")
        print("All updates complete.")
