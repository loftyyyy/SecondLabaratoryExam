# OS Concepts Simulator

A simple Python command-line program that simulates two classic Operating
Systems concepts:

- **CPU Scheduling** — First Come First Serve (FCFS, non-preemptive) and
  Round Robin (RR, preemptive)
- **Banker's Algorithm** — checks whether a system is in a safe state and,
  if so, prints a safe execution sequence

## Requirements

- Python 3.7 or higher (no external libraries needed — standard library only)

## How to Run

1. Clone or download this repository.
2. From the project folder, run:

   ```bash
   python3 SecondLabaratoryExam.py
   ```

3. Follow the on-screen menu and enter values when prompted.

## Menu Overview

```
1. CPU Scheduling Simulation
2. Banker's Algorithm (Safe State Check)
3. Exit
```

### 1. CPU Scheduling

You'll be asked to pick an algorithm, then enter each process's arrival
and burst time:

```
1. First Come First Serve (FCFS)  - Non-Preemptive
2. Round Robin (RR)               - Preemptive
```

Round Robin will additionally ask for a **Time Quantum**.

The program then prints:
- A Gantt chart showing execution order and timing
- A per-process table (arrival, burst, completion, waiting, turnaround)
- Average Waiting Time and Average Turnaround Time

**Example input** (4 processes, FCFS):

```
Enter number of processes: 4
  Arrival time: 0     Burst time: 5
  Arrival time: 1     Burst time: 3
  Arrival time: 2     Burst time: 8
  Arrival time: 3     Burst time: 6
```

### 2. Banker's Algorithm

You'll be asked for:
- Number of processes and number of resource types
- The **Allocation** matrix (resources currently held by each process)
- The **Maximum** matrix (maximum resources each process may need)
- The **Available** vector (resources currently free in the system)

The program computes the Need matrix (`Need = Max - Allocation`), runs the
safety algorithm, and prints whether the system is **safe** or **unsafe**,
along with a safe sequence if one exists.

**Example input** (classic 5-process, 3-resource example):

```
Enter number of processes: 5
Enter number of resource types: 3

Allocation:
  P0: 0 1 0
  P1: 2 0 0
  P2: 3 0 2
  P3: 2 1 1
  P4: 0 0 2

Maximum:
  P0: 7 5 3
  P1: 3 2 2
  P2: 9 0 2
  P3: 2 2 2
  P4: 4 3 3

Available: 3 3 2
```

**Expected output:**

```
Need Matrix:
P0: [7, 4, 3]
P1: [1, 2, 2]
P2: [6, 0, 0]
P3: [0, 1, 1]
P4: [4, 3, 1]

System is in a Safe State.
Safe Sequence: P1 → P3 → P4 → P0 → P2
```

## File Structure

```
.
├── os_simulator.py   # main program (CPU scheduling + Banker's Algorithm)
└── README.md
```

## Notes

- All input is entered interactively via the console — there are no
  command-line arguments or config files.
- The code is commented throughout to explain the scheduling and
  safety-algorithm logic.
