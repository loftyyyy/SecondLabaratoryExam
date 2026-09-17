#!/usr/bin/env python3
"""
os_simulator.py
================
A simple command-line simulation of two classic Operating Systems concepts:

1. CPU Scheduling
   - First Come First Serve (FCFS)       -> Non-Preemptive
   - Round Robin (RR)                    -> Preemptive

2. Banker's Algorithm
   - Checks whether a system (given Allocation, Max, and Available matrices)
     is in a SAFE or UNSAFE state, and prints a safe sequence if one exists.

Run the file and follow the on-screen menu:
    python3 os_simulator.py
"""

# ---------------------------------------------------------------------------
# Small helper utilities used by both modules
# ---------------------------------------------------------------------------

def get_int(prompt, min_value=None, max_value=None):
    """Repeatedly ask the user for an integer until a valid one is given.

    min_value / max_value let a caller restrict input to a range (e.g. a
    menu with only options 1-2) so a bad value can never slip through and
    crash the program later.
    """
    while True:
        try:
            value = int(input(prompt))
            if min_value is not None and value < min_value:
                print(f"  -> Please enter a value >= {min_value}.")
                continue
            if max_value is not None and value > max_value:
                print(f"  -> Please enter a value <= {max_value}.")
                continue
            return value
        except ValueError:
            print("  -> Invalid input, please enter a whole number.")


def print_header(title):
    """Pretty section header for readability in the console."""
    print("\n" + "=" * 60)
    print(title.center(60))
    print("=" * 60)


# ---------------------------------------------------------------------------
# PART 1: CPU SCHEDULING
# ---------------------------------------------------------------------------

class Process:
    """Simple data holder for a process and the results computed for it."""

    def __init__(self, pid, arrival, burst):
        self.pid = pid
        self.arrival = arrival
        self.burst = burst
        self.remaining = burst      # used for preemptive algorithms (RR)
        self.completion = 0
        self.waiting = 0
        self.turnaround = 0


def read_processes():
    """Collect process data (PID is auto-assigned P1, P2, ...)."""
    n = get_int("Enter number of processes: ", min_value=1)
    processes = []
    for i in range(n):
        print(f"\n--- Process P{i + 1} ---")
        arrival = get_int("  Arrival time: ", min_value=0)
        burst = get_int("  Burst time: ", min_value=1)
        processes.append(Process(f"P{i + 1}", arrival, burst))
    return processes


def print_results(processes, gantt_chart):
    """Common routine to display the Gantt chart and timing statistics."""

    # --- Gantt chart -------------------------------------------------
    # gantt_chart is a list of tuples: (pid, start_time, end_time)
    print("\nGantt Chart:")
    top = " | ".join(f"{pid:^5}" for pid, _, _ in gantt_chart)
    print(" " + top + " ")
    # Print the timeline markers (start time under each block, plus final end time)
    line = f"{gantt_chart[0][1]:<3}"
    for _, _, end in gantt_chart:
        line += f"{end:>9}"
    print(line)

    # --- Per-process table --------------------------------------------
    print(f"\n{'PID':<6}{'Arrival':<10}{'Burst':<8}{'Completion':<12}"
          f"{'Waiting':<10}{'Turnaround':<10}")
    total_wait = 0
    total_turnaround = 0
    for p in sorted(processes, key=lambda x: x.pid):
        print(f"{p.pid:<6}{p.arrival:<10}{p.burst:<8}{p.completion:<12}"
              f"{p.waiting:<10}{p.turnaround:<10}")
        total_wait += p.waiting
        total_turnaround += p.turnaround

    n = len(processes)
    print(f"\nAverage Waiting Time    : {total_wait / n:.2f}")
    print(f"Average Turnaround Time : {total_turnaround / n:.2f}")


def fcfs(processes):
    """
    First Come First Serve (Non-Preemptive)
    Logic: Sort processes by arrival time. Each process runs to completion
    in that order; if the CPU is idle waiting for the next arrival, time
    jumps forward to that arrival.
    """
    processes = sorted(processes, key=lambda p: p.arrival)
    time = 0
    gantt_chart = []

    for p in processes:
        # If CPU would be idle before this process arrives, skip ahead
        if time < p.arrival:
            time = p.arrival

        start = time
        time += p.burst          # process runs to completion, no preemption
        end = time

        p.completion = end
        p.turnaround = p.completion - p.arrival
        p.waiting = p.turnaround - p.burst

        gantt_chart.append((p.pid, start, end))

    return gantt_chart


def round_robin(processes, quantum):
    """
    Round Robin (Preemptive)
    Logic: Maintain a ready queue. Each process gets to run for at most
    `quantum` time units; if it doesn't finish, it goes to the back of the
    queue (after any processes that arrived during its slice). Repeat until
    all processes are finished.
    """
    processes = list(processes)
    n = len(processes)
    gantt_chart = []
    queue = []
    finished = 0

    # Sort by arrival to know arrival order
    remaining = sorted(processes, key=lambda p: p.arrival)

    # Start the clock at the first arrival
    time = remaining[0].arrival

    # Seed the queue with everyone who has arrived at "time"
    idx = 0
    while idx < n and remaining[idx].arrival <= time:
        queue.append(remaining[idx])
        idx += 1

    while finished < n:
        if not queue:
            # Nobody ready: jump forward to the next arrival
            time = remaining[idx].arrival
            queue.append(remaining[idx])
            idx += 1
            continue

        current = queue.pop(0)
        start = time
        run_time = min(quantum, current.remaining)
        time += run_time
        current.remaining -= run_time

        # Any process that arrives *during* this slice joins the queue now,
        # in arrival order, BEFORE the current process is re-queued.
        while idx < n and remaining[idx].arrival <= time:
            queue.append(remaining[idx])
            idx += 1

        end = time
        gantt_chart.append((current.pid, start, end))

        if current.remaining > 0:
            queue.append(current)   # not finished -> back of the queue
        else:
            current.completion = end
            current.turnaround = current.completion - current.arrival
            current.waiting = current.turnaround - current.burst
            finished += 1

    return gantt_chart


def merge_gantt(gantt_chart):
    """Merge consecutive identical-PID slices (can happen if a process is
    immediately re-picked) purely for a cleaner-looking chart."""
    if not gantt_chart:
        return gantt_chart
    merged = [gantt_chart[0]]
    for pid, start, end in gantt_chart[1:]:
        last_pid, last_start, last_end = merged[-1]
        if pid == last_pid and start == last_end:
            merged[-1] = (last_pid, last_start, end)
        else:
            merged.append((pid, start, end))
    return merged


def run_cpu_scheduling():
    print_header("CPU SCHEDULING SIMULATION")
    print("Choose a scheduling algorithm:")
    print("  1. First Come First Serve (FCFS)      - Non-Preemptive")
    print("  2. Round Robin (RR)                    - Preemptive")
    # max_value=2 guarantees `choice` can only ever be 1 or 2, so the
    # if/elif below is exhaustive and `gantt` is always assigned.
    choice = get_int("Enter choice (1-2): ", min_value=1, max_value=2)

    processes = read_processes()

    if choice == 1:
        gantt = fcfs(processes)
    else:  # choice == 2
        quantum = get_int("\nEnter Time Quantum: ", min_value=1)
        gantt = round_robin(processes, quantum)

    gantt = merge_gantt(gantt)
    print_results(processes, gantt)


# ---------------------------------------------------------------------------
# PART 2: BANKER'S ALGORITHM
# ---------------------------------------------------------------------------

def read_matrix(rows, cols, label):
    """Read a rows x cols matrix of non-negative integers from the user."""
    print(f"\nEnter the {label} matrix ({rows} processes x {cols} resources).")
    print("Enter each row as space-separated numbers, e.g.: 0 1 0")
    matrix = []
    for i in range(rows):
        while True:
            raw = input(f"  {label} for P{i}: ").split()
            try:
                row = [int(x) for x in raw]
                if len(row) != cols or any(x < 0 for x in row):
                    raise ValueError
                matrix.append(row)
                break
            except ValueError:
                print(f"  -> Please enter exactly {cols} non-negative integers.")
    return matrix


def read_vector(cols, label):
    """Read a single vector of length `cols` (e.g. Available resources)."""
    print(f"\nEnter the {label} vector ({cols} resource types).")
    while True:
        raw = input(f"  {label}: ").split()
        try:
            vector = [int(x) for x in raw]
            if len(vector) != cols or any(x < 0 for x in vector):
                raise ValueError
            return vector
        except ValueError:
            print(f"  -> Please enter exactly {cols} non-negative integers.")


def compute_need(max_matrix, allocation):
    """Need[i][j] = Max[i][j] - Allocation[i][j]  (resources still needed)."""
    n = len(max_matrix)
    m = len(max_matrix[0])
    return [[max_matrix[i][j] - allocation[i][j] for j in range(m)] for i in range(n)]


def bankers_algorithm(n_processes, n_resources, allocation, max_matrix, available):
    """
    Runs the Banker's Algorithm safety check.

    Logic:
      1. Compute the Need matrix (Max - Allocation).
      2. Start with Work = Available, and mark all processes as unfinished.
      3. Repeatedly look for an unfinished process whose Need <= Work.
         If found: pretend it runs to completion, add its Allocation back
         into Work (resources released), mark it finished, add it to the
         safe sequence, and restart the scan.
      4. If a full pass finds no such process but some remain unfinished,
         the system is UNSAFE.
      5. If every process gets finished, the system is SAFE and the order
         in which they finished is a valid safe sequence.
    """
    need = compute_need(max_matrix, allocation)
    work = available[:]                      # copy of available resources
    finished = [False] * n_processes
    safe_sequence = []

    while len(safe_sequence) < n_processes:
        progress_made = False

        for i in range(n_processes):
            if finished[i]:
                continue

            # Can process i's remaining need be satisfied by current Work?
            if all(need[i][j] <= work[j] for j in range(n_resources)):
                # Simulate process i running to completion and releasing
                # all of its currently allocated resources back to Work.
                for j in range(n_resources):
                    work[j] += allocation[i][j]

                finished[i] = True
                safe_sequence.append(f"P{i}")
                progress_made = True

        if not progress_made:
            # No process could be satisfied this pass -> deadlock possible
            return False, safe_sequence

    return True, safe_sequence


def run_bankers_algorithm():
    print_header("BANKER'S ALGORITHM - SAFE STATE CHECK")

    n_processes = get_int("Enter number of processes: ", min_value=1)
    n_resources = get_int("Enter number of resource types: ", min_value=1)

    allocation = read_matrix(n_processes, n_resources, "Allocation")
    max_matrix = read_matrix(n_processes, n_resources, "Maximum")

    # Sanity check: Allocation must never exceed Max for any process
    for i in range(n_processes):
        for j in range(n_resources):
            if allocation[i][j] > max_matrix[i][j]:
                print(f"\n  -> Error: Allocation of P{i} exceeds its Max "
                      f"for resource {j}. Please re-check your input.")
                return

    available = read_vector(n_resources, "Available")

    need = compute_need(max_matrix, allocation)

    # Display computed Need matrix for transparency, one row per process
    # e.g.  P0: [7, 4, 3]
    print("\nNeed Matrix:")
    for i, row in enumerate(need):
        print(f"P{i}: {row}")

    is_safe, sequence = bankers_algorithm(
        n_processes, n_resources, allocation, max_matrix, available
    )

    print()  # blank line before the final verdict, as in the sample output
    if is_safe:
        print("System is in a Safe State.")
        print("Safe Sequence: " + " \u2192 ".join(sequence))
    else:
        # `sequence` still holds whichever processes could be finished
        # before the algorithm got stuck, which is useful diagnostic info.
        print("System is in an Unsafe State (no safe sequence exists).")
        if sequence:
            print("Processes that could still be safely finished: "
                  + " \u2192 ".join(sequence))
        print("Deadlock is possible with the remaining processes.")


# ---------------------------------------------------------------------------
# MAIN MENU
# ---------------------------------------------------------------------------

def main():
    while True:
        print_header("OPERATING SYSTEMS CONCEPTS SIMULATOR")
        print("1. CPU Scheduling Simulation")
        print("2. Banker's Algorithm (Safe State Check)")
        print("3. Exit")
        choice = get_int("Select an option (1-3): ", min_value=1, max_value=3)

        if choice == 1:
            run_cpu_scheduling()
        elif choice == 2:
            run_bankers_algorithm()
        else:
            print("\nGoodbye!")
            break

        input("\nPress Enter to return to the main menu...")


if __name__ == "__main__":
    main()
