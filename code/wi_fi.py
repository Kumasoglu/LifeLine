import network
import urequests
import time
import uhashlib

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

class Senko:
    raw = "https://raw.githubusercontent.com"
    github = "https://github.com"

    def __init__(self, user, repo, url=None, branch="main", working_dir="code", files=["boot.py", "main.py", "circullarBuffer.py", "ecg_filters.py", "heartRate.py", "wi_fi.py", "backup.py"], headers={}):
        """Senko OTA agent class.

        Args:
            user (str): GitHub user.
            repo (str): GitHub repo to fetch.
            branch (str): GitHub repo branch. (master)
            working_dir (str): Directory inside GitHub repo where the micropython app is.
            url (str): URL to root directory.
            files (list): Files included in OTA update.
            headers (list, optional): Headers for urequests.
        """
        self.base_url = "{}/{}/{}".format(self.raw, user, repo) if user else url.replace(self.github, self.raw)
        self.url = url if url is not None else "{}/{}/{}".format(self.base_url, branch, working_dir)
        self.headers = headers
        self.files = files

    def _check_hash(self, x, y):
        x_hash = uhashlib.sha1(x.encode())
        y_hash = uhashlib.sha1(y.encode())

        x = x_hash.digest()
        y = y_hash.digest()

        if str(x) == str(y):
            return True
        else:
            return False

    def _get_file(self, url):
        payload = urequests.get(url, headers=self.headers)
        code = payload.status_code

        if code == 200:
            return payload.text
        else:
            return None

    def _check_all(self):
        changes = []

        for file in self.files:
            latest_version = self._get_file(self.url + "/" + file)
            if latest_version is None:
                continue

            try:
                with open(file, "r") as local_file:
                    local_version = local_file.read()
            except:
                local_version = ""

            if not self._check_hash(latest_version, local_version):
                changes.append(file)

        return changes

    def fetch(self):
        """Check if newer version is available.

        Returns:
            True - if is, False - if not.
        """
        if not self._check_all():
            return False
        else:
            return True

    def update(self):
        """Replace all changed files with newer one.

        Returns:
            True - if changes were made, False - if not.
        """
        changes = self._check_all()

        for file in changes:
            with open(file, "w") as local_file:
                local_file.write(self._get_file(self.url + "/" + file))

        if changes:
            return True
        else:
            return False

