> （2024）多数显卡在高负载下的可接受温度为70°C至85°C（？？？）

针对当前机器（非机房环境，室温约 26°C，机箱内较空，整体风道和机箱风扇未能充分发挥散热效果），在进行大模型推理性能的压力测试时，GPU 利用率和功耗均处于满载状态，而 CPU 基本处于低负载。此情况下，显卡核心温度维持在 **85°C～90°C**，温度偏高（在使用租用平台的同类显卡、运行相同压力测试程序时，显卡温度明显更低，推测与其机房环境及大量工业级散热风扇有关）。

值得注意的是，在上述工况下，GPU 风扇转速仅约 65%，CPU 相关风扇转速更是长期保持在较低水平。



这里参考[Linux NVIDIA（英伟达） GPU 风扇转速控制教程](https://www.bilibili.com/opus/948063882581114884)，对当前双卡A6000的风扇转速进行控制，不同的温度对应不同的风扇转速：

```
temperature_points = [0, 40, 57, 70]
fan_speed_points = [27, 40, 80, 100]
```

示例代码如下：

```python
import time
from pynvml import *
import os
import signal

# Fan curve parameters
temperature_points = [0, 40, 57, 70]
fan_speed_points = [27, 40, 80, 100]

# GPU selection for fan curve application
gpus = []

# Enable or disable GPU Validation
GPU_VALIDATION_SETTINGS = {
    'ENABLE': False,
    'SHOW_INVALID_INDICES': True
}

# Sleep interval
sleep_seconds = 5

# Temperature hysteresis
temperature_hysteresis = 5

# Initialize nvml
nvmlInit()

# Get device count
device_count = nvmlDeviceGetCount()

# Validate GPUs
if GPU_VALIDATION_SETTINGS['ENABLE']:
    if not gpus:
        gpus = list(range(device_count))
    else:
        invalid_gpus = [gpu for gpu in gpus if gpu >= device_count or gpu < 0]
        if invalid_gpus and GPU_VALIDATION_SETTINGS['SHOW_INVALID_INDICES']:
            print(f"ERROR: Invalid GPU index found:{invalid_gpus}")
            print(f"Your system has {device_count} GPUs, and indexes range from 0 to {device_count - 1}.")
            print(f"Please check your gpus settings and correct the invalid index.（＾ｖ＾）")
        elif invalid_gpus:
            print("ERROR: Invalid GPU index found")
            print(f"Your system has {device_count} GPUs, and indexes range from 0 to {device_count - 1}.")
            print(f"If you want to display specific invalid indexes, set 'SHOW_INVALID_INDICES' to 'True' ")
            print(f"Please check your gpus settings and correct the invalid index.（＾ｖ＾）")
        if invalid_gpus:
            nvmlShutdown()
            exit(1)
    if not gpus and device_count > 0:
        print("Warning: No valid GPU selected. Controlling all detected GPUs.")
        gpus = list(range(device_count))
    elif not gpus and device_count == 0:
        print("Error: No GPUs found in the system.（＾ｖ＾）")
        nvmlShutdown()
        exit(1)
elif not gpus:
    gpus = list(range(device_count))

# Print driver version and device info
print("============================================================")
print(f"Driver Version: {nvmlSystemGetDriverVersion()}")

gpu_info = []
for i in range(device_count):
    handle = nvmlDeviceGetHandleByIndex(i)
    name = nvmlDeviceGetName(handle)
    fan_count = nvmlDeviceGetNumFans(handle)
    if i in gpus:
        gpu_info.append({'handle': handle, 'fan_count': fan_count, 'index': i, 'name': name, 'setted_fan_speed': fan_speed_points[0]})
        print(f"Controlling GPU {i}: {name}, Fan Count: {fan_count}")
    else:
        print(f"Skipping GPU {i}: {name}")

if not gpu_info:
    print("Error: No valid GPUs to control based on your settings.（＾ｖ＾）")
    nvmlShutdown()
    exit(1)

# Validate temperature and fan speed points
if len(temperature_points) != len(fan_speed_points):
    raise ValueError("temperature_points and fan_speed_points must have the same length")
else:
    num_total_curve_point = len(temperature_points)

for i in range(len(temperature_points) - 1):
    if temperature_points[i] >= temperature_points[i + 1]:
        raise ValueError("temperature_points must be strictly increasing")
    if fan_speed_points[i] > fan_speed_points[i + 1]:
        raise ValueError("fan_speed_points must be increasing")

# Set initial fan speed and enable manual control for selected GPUs
for gpu in gpu_info:
    for i in range(gpu['fan_count']):
        nvmlDeviceSetFanSpeed_v2(gpu['handle'], i, fan_speed_points[0])
    gpu['setted_fan_speed'] = fan_speed_points[0]

# Function to clear lines
def clear_lines(num_lines):
    for _ in range(num_lines):
        print('\033[1A\033[K', end='')

# Function to print info
def print_info(info):
    lines = info.split('\n')
    for line in lines:
        print(line)
    return len(lines)

# Main loop
last_lines = 0
terminate = False

def signal_handler(sig, frame):
    global terminate
    terminate = True

signal.signal(signal.SIGTERM, signal_handler)

try:
    while not terminate:
        all_info_lines = 0
        for gpu in gpu_info:
            handle = gpu['handle']
            fan_count = gpu['fan_count']
            index = gpu['index']
            setted_fan_speed = gpu['setted_fan_speed']

            # Get temperature
            temperature = nvmlDeviceGetTemperature(handle, NVML_TEMPERATURE_GPU)
            if temperature is None:
                continue

            # Calculate fan speed
            point = 0
            while point < num_total_curve_point - 1 and temperature >= temperature_points[point + 1]:
                point += 1

            previous_point = max(0, point)
            next_point = min(num_total_curve_point - 1, point + 1)

            temperature_delta = temperature_points[next_point] - temperature_points[previous_point]
            fan_speed_delta = fan_speed_points[next_point] - fan_speed_points[previous_point]
            temperature_increment = temperature - temperature_points[previous_point]
            fan_speed_increment = fan_speed_delta * temperature_increment / temperature_delta if temperature_delta != 0 else 0
            fan_speed = round(fan_speed_points[previous_point] + fan_speed_increment)

            step_down_temperature = temperature - temperature_hysteresis

            info = f"""==================== GPU {index} ({gpu['name']}) ====================
Temperature: {temperature}°C
Total Curve Point: {num_total_curve_point}
Current Curve Point: {point}
Previous_Curve_Point: {previous_point}
Next_Curve_Point: {next_point}
Fan_Speed: {fan_speed}%
============================================================
Temperature_Delta: {temperature_delta}
Fan_Speed_Delta: {fan_speed_delta}
Temperature_Increment: {temperature_increment}
Fan_Speed_Increment: {fan_speed_increment}
Step_Down_Temperature: {step_down_temperature}
============================================================"""

            # Print information
            print(info)
            all_info_lines += len(info.split('\n'))

            # Set fan speed if different
            if fan_speed != setted_fan_speed:
                for i in range(fan_count):
                    nvmlDeviceSetFanSpeed_v2(handle, i, fan_speed)
                gpu['setted_fan_speed'] = fan_speed

        # Clear previous output
        clear_lines(last_lines)
        last_lines = all_info_lines

        time.sleep(sleep_seconds)
finally:
    # Reset to auto fan control
    for gpu in gpu_info:
        for i in range(gpu['fan_count']):
            nvmlDeviceSetDefaultFanSpeed_v2(gpu['handle'], i)
    nvmlShutdown()

```

实测有效，两张卡温度都在75度以下了。



其他注意事项：

- 室内温度
- 机箱风扇设计：是否可以形成风压