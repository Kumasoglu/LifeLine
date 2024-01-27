import time

class BPMMonitor:
    def __init__(self, sample_rate, threshold):
        self.sample_rate = sample_rate
        self.threshold = threshold
        self.signal_window = []  # Stores the last 5 ECG values
        self.sample_window = 5
        self.last_peak_time = None
        self.r_peak_intervals = []  # Stores intervals between R-peaks

    def update(self, value):
        current_time = time.ticks_ms()

        # Update the signal window with the new value
        self.signal_window.append(value)
        if len(self.signal_window) > self.sample_window:
            self.signal_window.pop(0)

        # Check if the middle value is the highest and above the threshold
        if len(self.signal_window) == self.sample_window:
            middle_value = self.signal_window[self.sample_window // 2]
            if middle_value == max(self.signal_window) and middle_value > self.threshold:
                if self.last_peak_time is not None:
                    interval_ms = time.ticks_diff(current_time, self.last_peak_time)
                    self.r_peak_intervals.append(interval_ms)

                # Update the last peak time
                self.last_peak_time = current_time

        # Calculate average BPM from the last 8 R-peak intervals
        if len(self.r_peak_intervals) == 10:
            avg_bpm = self.calculate_average_bpm()
            self.r_peak_intervals = []  # Reset for the next set of 8 R-peaks
            return avg_bpm

    def calculate_average_bpm(self):
        total_bpm = 0
        for interval_ms in self.r_peak_intervals:
            interval_seconds = interval_ms / 1000  # Convert milliseconds to seconds
            if interval_seconds > 0:
                total_bpm += 60 / interval_seconds
        return total_bpm / len(self.r_peak_intervals)


