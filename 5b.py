import threading
import time

# Global arrays as required [cite: 694]
original_list = [7, 12, 19, 3, 18, 4, 2, 6, 15, 8]
sorted_array = [0] * len(original_list)
mid_index = len(original_list) // 2

# Sub-results storage
left_sorted = []
right_sorted = []

def sort_sublist(start_idx, end_idx, is_left):
    global left_sorted, right_sorted
    sublist = original_list[start_idx:end_idx]
    # Simulate work
    time.sleep(0.1)
    sublist.sort()
    
    if is_left:
        left_sorted = sublist
        print(f"Thread 1 (Left) Sorted: {left_sorted}")
    else:
        right_sorted = sublist
        print(f"Thread 2 (Right) Sorted: {right_sorted}")

def merge_thread():
    # Wait for sub-sorts to finish (simulated by logic flow in main)
    global sorted_array
    print("Merge Thread Started...")
    
    i = j = k = 0
    while i < len(left_sorted) and j < len(right_sorted):
        if left_sorted[i] < right_sorted[j]:
            sorted_array[k] = left_sorted[i]
            i += 1
        else:
            sorted_array[k] = right_sorted[j]
            j += 1
        k += 1
        
    # Copy remaining
    while i < len(left_sorted):
        sorted_array[k] = left_sorted[i]
        i += 1; k += 1
    while j < len(right_sorted):
        sorted_array[k] = right_sorted[j]
        j += 1; k += 1
        
    print(f"Merge Complete: {sorted_array}")

def solve_task5b():
    print(f"Original: {original_list}")
    
    # Create Sorting Threads [cite: 692]
    t1 = threading.Thread(target=sort_sublist, args=(0, mid_index, True))
    t2 = threading.Thread(target=sort_sublist, args=(mid_index, len(original_list), False))
    
    t1.start()
    t2.start()
    
    t1.join()
    t2.join()
    
    # Create Merging Thread [cite: 697]
    t3 = threading.Thread(target=merge_thread)
    t3.start()
    t3.join()

if __name__ == "__main__":
    solve_task5b()