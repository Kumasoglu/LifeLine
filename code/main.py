from machine import Timer, Pin, ADC, SoftI2C, reset
import time
from wi_fi import WiFiConnection, Senko  
from circullarBuffer import CircularBuffer
from ecg_filters import Filter
from heartRate import BPMMonitor
from accel import ADXL345
import gc

# Garbage Collection
gc.collect()
gc.enable()

# Connecting to Wi-Fi
wifi = WiFiConnection('osman', 'gevtbt0651')

if wifi.connect():
    
    ota = Senko(user="Kumasoglu", repo="LifeLine", working_dir="code", files=["boot.py", "main.py", "circullarBuffer.py", "ecg_filters.py", "heartRate.py", "wi_fi.py", "backup.py"])
    
    if ota.fetch():
        print("Updates available. Updating...")
        if ota.update():
            print("Update successful! Rebooting...")
            time.sleep(10)
            reset()
    else:
        print("No updates available.")
        time.sleep(10)
else:
    print("Proceeding without Wi-Fi connection. No updates made")
    time.sleep(10)


# Give power to ADXL345 Sensor
aclPowerPin = Pin(4, Pin.OUT)
aclPowerPin.value(1)

# Turn Off the LED at mcu
LED_Pin = Pin(15, Pin.OUT)
LED_Pin.value(0)


# Configure ADC
adc_pin = 34
adc = ADC(Pin(adc_pin, Pin.IN))
adc.atten(ADC.ATTN_11DB)  # 0 - 3.3V
adc.width(ADC.WIDTH_12BIT)  # 12 bit resolution (0-4096 different points for 1 point)

# Define pin for y of the accelerometer
ypin = ADC(Pin(33))  # A3

# Sampling Settings
Sampling_Period = 5  # Sampling Frequency = 200 Hz

# Circular buffer for storing ADC values
buffer_size = 200  # Buffer takes 1.25 seconds to fill
adc_data = CircularBuffer(buffer_size)

# (3rd Order and 4th Order)
b_lp = [0.04658291, 0.18633163, 0.27949744, 0.18633163, 0.04658291]
a_lp = [1.0, -0.7820952, 0.67997853, -0.1826757, 0.03011888]

b_hp = [0.96907117, -2.90721352, 2.90721352, -0.96907117]
a_hp = [1.0, -2.93717073, 2.87629972, -0.93909894]


# Create filter instances
lp_filter = Filter(b_lp, a_lp)
hp_filter = Filter(b_hp, a_hp)

# Define I2C pins
i2c = SoftI2C(sda=Pin(21), scl=Pin(22))

# BPM Monitor instance creation
bpm_monitor = BPMMonitor(sample_rate=200, threshold=650)

# Initialize ADXL345
accel = ADXL345(i2c)

# Interrupt Service Routine
def isr(timer):
    adc_value = adc.read_uv() / 1000  # Converting micro-volt to mili-volt. Ease of interpretation and further processing, as millivolts are a more commonly used unit in many applications, including ECG signal analysis.
    adc_data.enqueue(adc_value)

# Filter Raw ECG Data
def process_ecg_data(raw_value):
    filtered_sample = lp_filter.filter(raw_value)
    filtered_sample = hp_filter.filter(filtered_sample)
    return filtered_sample


# Setup timer
ecg_timer = Timer(0)
ecg_timer.init(period=Sampling_Period, mode=Timer.PERIODIC, callback=isr)

# Main Program Loop
try:
    last_processed_time_ms = None
    last_bpm = None  # Variable to hold the last calculated BPM

    while True:
        while not adc_data.is_empty():
            raw_ecg_value = adc_data.dequeue()
            filtered_ecg_value = process_ecg_data(raw_ecg_value)
            current_time_ms = time.ticks_ms()
            y = accel.read_y()
            if last_processed_time_ms is None or time.ticks_diff(current_time_ms, last_processed_time_ms) >= 5:
                last_processed_time_ms = current_time_ms
                bpm = bpm_monitor.update(filtered_ecg_value)
                if bpm is not None:
                    last_bpm = bpm  # Update the BPM only if a new value is calculated
            print(filtered_ecg_value)

except KeyboardInterrupt:
    ecg_timer.deinit()  # Stop the timer to prevent further interrupts



