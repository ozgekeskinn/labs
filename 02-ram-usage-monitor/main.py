import os
import psutil
import time

process = psutil.Process(os.getpid())

def get_ram_usage():
    memory_bytes = process.memory_info().rss
    return memory_bytes / 1_000_000

steps = ["Initial"]
ram_history = [get_ram_usage()]
print(f"Initial RAM Usage: {ram_history[0]:.2f} MB")

allocated_lists = []
for step in range(1,4):
    numbers = list(range(500_000))
    allocated_lists.append(numbers)
    current_ram = get_ram_usage()

    steps.append(f"Step {step}")
    ram_history.append(current_ram)
    print(f"Step {step}: RAM Usage: {current_ram:.2f} MB")
    time.sleep(1)

print("\nMEMORY RELEASE TEST")
allocated_lists.clear()
del numbers
time.sleep(1)

after_cleanup = get_ram_usage()
steps.append("After Cleanup")
ram_history.append(after_cleanup)
print(f"After cleanup: RAM Usage: {after_cleanup:.2f} MB")

import matplotlib.pyplot as plt
plt.figure(figsize = (10,5))
plt.plot(steps, ram_history, marker = "o", linewidth = 2)

plt.title("Python Process RAM Usage")
plt.xlabel("Benchmark Steps")
plt.ylabel("RAM Usage (MB)")

plt.grid(True, alpha = 0.3)
plt.tight_layout()
plt.savefig("memory_usage.png", dpi = 160)
plt.show()