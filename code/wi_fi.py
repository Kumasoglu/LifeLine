import network
import urequest

class WiFiConnection:
    def __init__(self, ssid, password):
        self.ssid = ssid
        self.password = password
        self.wlan = network.WLAN(network.STA_IF)
        
    def connect(self):
        if not self.wlan.isconnected():
            self.wlan.active(True)
            self.wlan.connect(self.ssid, self.password)
            while not self.wlan.isconnected():
                pass
        print("Connected to Wi-Fi")
        

class OTAUpdater:
    def __init__(self, files_to_update):
        self.files_to_update = files_to_update

    def update(self):
        for file_info in self.files_to_update:
            url = file_info["url"]
            dest = file_info["dest"]
            response = urequests.get(url)
            if response.status_code == 200:  # OK
                with open(dest, 'w') as f:
                    f.write(response.text)
                print(f"Updated {dest}")
            else:
                print(f"Failed to download {url}")
        print("All updates complete.")
