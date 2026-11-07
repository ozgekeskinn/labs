from array import array
import time
import random 
import statistics

SIZE = 1_000_000
# SIZE = 100_000
# SIZE = 5_000_000

# Dizi oluşturulur
numbers = array("q", range(SIZE))

# Rastgele erişim sırası hazırlanır
indices = list(range(SIZE))
random.shuffle(indices)

# Ölçüm sonuçlarını tutacak listeler oluşturulur
sequential_times = []
random_times = []

for repeat in range(5):
    # Sıralı Erişim
    start = time.perf_counter()
    sequential_total = 0
    for i in range(SIZE):
        sequential_total += numbers[i]
    
    sequential_time = time.perf_counter() - start
    sequential_times.append(sequential_time)

    # Rastgele Erişim
    start = time.perf_counter()
    random_total = 0
    for i in indices:
        random_total += numbers[i]
    random_time = time.perf_counter() - start
    random_times.append(random_time)

    assert sequential_total == random_total

    print(
        f"Run {repeat + 1}:"
        f"Sequential = {sequential_time:.4f}s | "
        f"Random = {random_time:.4f}s"
    )

sequential_median = statistics.median(sequential_times)
random_median = statistics.median(random_times)

print("\n===== BENCHMARK RESULTS =====")
print(f"Sequential median: {sequential_median:.4f}s")
print(f"Random median: {random_median:.4f}s")
print(f"Random / Sequential: {random_median / sequential_median:.2f}x")

if random_median > sequential_median:
    print("Random access is slower, potentially due to cache misses and memory access overhead.")
else:
    print("Random access was not slower in this benchmark.")