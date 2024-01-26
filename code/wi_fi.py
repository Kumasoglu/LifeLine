import network
import urequests
import time
import gc

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

    def update_file(self, url, dest):
        try:
            response = urequests.get(url, stream=True)
            if response.status_code == 200:
                with open(dest, 'w') as f:
                    for chunk in response.iter_content(1024):  # Read in chunks of 1KB
                        f.write(chunk)
                response.close()
                print(f"Updated {dest}")
            else:
                print(f"Failed to download {url}")
        except Exception as e:
            print(f"Error updating {dest}: {e}")
        gc.collect()  # Trigger garbage collection after updating each file

    def update(self):
        for file in self.file_list:
            url = f"{self.base_url}/{file}"
            self.update_file(url, file)
        print("All updates complete.")
