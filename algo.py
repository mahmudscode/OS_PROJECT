import tkinter as tk
from tkinter import ttk, messagebox

# CPU Scheduling Algorithms
def fcfs(processes, arrival, burst):
    n = len(processes)
    # Sort by arrival time
    proc_data = list(zip(processes, arrival, burst, range(n)))
    proc_data.sort(key=lambda x: x[1])
    
    start_time = [0]*n
    completion_time = [0]*n
    waiting_time = [0]*n
    turnaround_time = [0]*n
    
    current_time = 0
    for i in range(n):
        proc, arr, bur, orig_idx = proc_data[i]
        if current_time < arr:
            current_time = arr
        start_time[orig_idx] = current_time
        completion_time[orig_idx] = current_time + bur
        turnaround_time[orig_idx] = completion_time[orig_idx] - arr
        waiting_time[orig_idx] = turnaround_time[orig_idx] - bur
        current_time = completion_time[orig_idx]
    
    return start_time, completion_time, waiting_time, turnaround_time

def sjf_with_at(processes, arrival, burst):
    n = len(processes)
    completed = [False]*n
    current_time = 0
    start_time = [0]*n
    completion_time = [0]*n
    waiting_time = [0]*n
    turnaround_time = [0]*n
    completed_count = 0

    while completed_count < n:
        idx = -1
        min_burst = float('inf')
        
        # Find process with shortest burst time that has arrived
        for i in range(n):
            if arrival[i] <= current_time and not completed[i] and burst[i] < min_burst:
                min_burst = burst[i]
                idx = i
        
        if idx == -1:
            current_time += 1
            continue
        
        start_time[idx] = current_time
        current_time += burst[idx]
        completion_time[idx] = current_time
        turnaround_time[idx] = completion_time[idx] - arrival[idx]
        waiting_time[idx] = turnaround_time[idx] - burst[idx]
        completed[idx] = True
        completed_count += 1

    return start_time, completion_time, waiting_time, turnaround_time

def sjf_without_at(processes, burst):
    n = len(processes)
    # Create list of (process_name, burst_time, original_index)
    proc_data = list(zip(processes, burst, range(n)))
    proc_data.sort(key=lambda x: x[1])
    
    start_time = [0]*n
    completion_time = [0]*n
    waiting_time = [0]*n
    turnaround_time = [0]*n
    current_time = 0

    for proc, bur, orig_idx in proc_data:
        start_time[orig_idx] = current_time
        completion_time[orig_idx] = current_time + bur
        turnaround_time[orig_idx] = completion_time[orig_idx]
        waiting_time[orig_idx] = start_time[orig_idx]
        current_time = completion_time[orig_idx]

    return start_time, completion_time, waiting_time, turnaround_time

def priority_scheduling(processes, arrival, burst, priority):
    n = len(processes)
    completed = [False]*n
    current_time = 0
    start_time = [0]*n
    completion_time = [0]*n
    waiting_time = [0]*n
    turnaround_time = [0]*n
    completed_count = 0

    while completed_count < n:
        idx = -1
        highest_priority = float('inf')
        
        # Find highest priority process (lower number = higher priority)
        for i in range(n):
            if arrival[i] <= current_time and not completed[i] and priority[i] < highest_priority:
                highest_priority = priority[i]
                idx = i
        
        if idx == -1:
            current_time += 1
            continue
        
        start_time[idx] = current_time
        current_time += burst[idx]
        completion_time[idx] = current_time
        turnaround_time[idx] = completion_time[idx] - arrival[idx]
        waiting_time[idx] = turnaround_time[idx] - burst[idx]
        completed[idx] = True
        completed_count += 1

    return start_time, completion_time, waiting_time, turnaround_time

def round_robin(processes, arrival, burst, quantum):
    n = len(processes)
    remaining = burst.copy()
    current_time = 0
    completion_time = [0]*n
    start_time = [-1]*n
    ready_queue = []
    visited = [False]*n
    
    # Sort processes by arrival time
    proc_indices = list(range(n))
    proc_indices.sort(key=lambda x: arrival[x])
    
    i = 0
    while True:
        # Add newly arrived processes to ready queue
        while i < n and arrival[proc_indices[i]] <= current_time:
            if not visited[proc_indices[i]]:
                ready_queue.append(proc_indices[i])
                visited[proc_indices[i]] = True
            i += 1
        
        if not ready_queue:
            if i < n:
                current_time = arrival[proc_indices[i]]
                continue
            else:
                break
        
        idx = ready_queue.pop(0)
        
        if start_time[idx] == -1:
            start_time[idx] = current_time
        
        if remaining[idx] > quantum:
            current_time += quantum
            remaining[idx] -= quantum
            
            # Add newly arrived processes before re-adding current process
            temp_i = i
            while temp_i < n and arrival[proc_indices[temp_i]] <= current_time:
                if not visited[proc_indices[temp_i]]:
                    ready_queue.append(proc_indices[temp_i])
                    visited[proc_indices[temp_i]] = True
                    i = temp_i + 1
                temp_i += 1
            
            ready_queue.append(idx)
        else:
            current_time += remaining[idx]
            remaining[idx] = 0
            completion_time[idx] = current_time

    waiting_time = [completion_time[i] - arrival[i] - burst[i] for i in range(n)]
    turnaround_time = [completion_time[i] - arrival[i] for i in range(n)]
    
    return start_time, completion_time, waiting_time, turnaround_time

# GUI Implementation
class CPUSchedulingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CPU Scheduling Algorithms")
        self.root.geometry("1080x1920")
        
        self.algorithms = ["FCFS", "SJF with AT", "SJF without AT", "Priority Scheduling", "Round Robin"]
        self.selected_algo = tk.StringVar(value=self.algorithms[0])
        
        # Theme configuration
        self.is_dark_mode = True
        self.themes = {
            'dark': {
                'bg': '#2E3440',
                'fg': '#D8DEE9',
                'title_fg': '#88C0D0',
                'output_bg': '#3B4252',
                'output_fg': '#ECEFF4',
                'button_bg': '#81A1C1',
                'button_fg': 'black',
                'entry_bg': 'white',
                'entry_fg': 'black'
            },
            'light': {
                'bg': '#F5F5F5',
                'fg': '#2E3440',
                'title_fg': '#0066CC',
                'output_bg': '#FFFFFF',
                'output_fg': '#000000',
                'button_bg': '#4A90E2',
                'button_fg': 'white',
                'entry_bg': 'white',
                'entry_fg': 'black'
            }
        }
        
        self.root.configure(bg=self.themes['dark']['bg'])
        self.create_widgets()

    def create_widgets(self):
        # Get current theme
        theme = self.themes['dark'] if self.is_dark_mode else self.themes['light']
        
        # Create main container frame centered in the window
        self.main_frame = tk.Frame(self.root, bg=theme['bg'])
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center")

        label_style = {"bg": theme['bg'], "fg": theme['fg'], "font":("Arial", 14, "bold")}
        entry_style = {"width":50, "font":("Arial", 12), "bg": theme['entry_bg'], "fg": theme['entry_fg']}

        # Title and Theme Button Container
        title_frame = tk.Frame(self.main_frame, bg=theme['bg'])
        title_frame.grid(row=0, column=0, columnspan=2, pady=30)
        
        # Title
        self.title_label = tk.Label(title_frame, text="CPU Scheduling Algorithms", 
                               bg=theme['bg'], fg=theme['title_fg'], font=("Arial", 24, "bold"))
        self.title_label.pack(side="left", padx=(0, 20))
        
        # Theme Toggle Button
        self.theme_button = tk.Button(title_frame, text="☀️ Light Mode" if self.is_dark_mode else "🌙 Dark Mode", 
                                      bg=theme['button_bg'], fg=theme['button_fg'], 
                                      font=("Arial", 12, "bold"), command=self.toggle_theme, 
                                      padx=20, pady=10, cursor="hand2")
        self.theme_button.pack(side="left")

        # Algorithm selection
        self.algo_label = tk.Label(self.main_frame, text="Select Algorithm:", **label_style)
        self.algo_label.grid(row=1, column=0, padx=10, pady=15, sticky="e")
        self.algo_menu = ttk.Combobox(self.main_frame, values=self.algorithms, textvariable=self.selected_algo, 
                                      width=48, font=("Arial", 12))
        self.algo_menu.grid(row=1, column=1, padx=10, pady=15, sticky="w")

        # Number of processes input
        self.num_label = tk.Label(self.main_frame, text="Number of Processes:", **label_style)
        self.num_label.grid(row=2, column=0, padx=10, pady=15, sticky="e")
        self.num_processes_entry = tk.Entry(self.main_frame, **entry_style)
        self.num_processes_entry.grid(row=2, column=1, padx=10, pady=15, sticky="w")

        # Burst times input
        self.burst_label = tk.Label(self.main_frame, text="Burst Times (e.g., 5,3,8):", **label_style)
        self.burst_label.grid(row=3, column=0, padx=10, pady=15, sticky="e")
        self.burst_entry = tk.Entry(self.main_frame, **entry_style)
        self.burst_entry.grid(row=3, column=1, padx=10, pady=15, sticky="w")

        # Arrival times input
        self.arrival_label = tk.Label(self.main_frame, text="Arrival Times (optional, e.g., 0,1,2):", **label_style)
        self.arrival_label.grid(row=4, column=0, padx=10, pady=15, sticky="e")
        self.arrival_entry = tk.Entry(self.main_frame, **entry_style)
        self.arrival_entry.grid(row=4, column=1, padx=10, pady=15, sticky="w")

        # Priority input
        self.priority_label = tk.Label(self.main_frame, text="Priority (for Priority Scheduling):", **label_style)
        self.priority_label.grid(row=5, column=0, padx=10, pady=15, sticky="e")
        self.priority_entry = tk.Entry(self.main_frame, **entry_style)
        self.priority_entry.grid(row=5, column=1, padx=10, pady=15, sticky="w")

        # Time quantum input
        self.quantum_label = tk.Label(self.main_frame, text="Time Quantum (for Round Robin):", **label_style)
        self.quantum_label.grid(row=6, column=0, padx=10, pady=15, sticky="e")
        self.quantum_entry = tk.Entry(self.main_frame, **entry_style)
        self.quantum_entry.grid(row=6, column=1, padx=10, pady=15, sticky="w")

        # Run button
        self.run_button = tk.Button(self.main_frame, text="Run Algorithm", bg=theme['button_bg'], fg=theme['button_fg'], 
                                    font=("Arial", 16, "bold"), command=self.run_algorithm, 
                                    padx=40, pady=15, cursor="hand2")
        self.run_button.grid(row=7, column=0, columnspan=2, pady=30)

        # Output text area
        self.output_text = tk.Text(self.main_frame, height=25, width=110, bg=theme['output_bg'], fg=theme['output_fg'], 
                                   font=("Courier", 11), relief="solid", borderwidth=2)
        self.output_text.grid(row=8, column=0, columnspan=2, padx=10, pady=20)

        # Scrollbar for output
        self.scrollbar = tk.Scrollbar(self.main_frame, command=self.output_text.yview)
        self.scrollbar.grid(row=8, column=2, sticky="ns", pady=20)
        self.output_text.config(yscrollcommand=self.scrollbar.set)

    def run_algorithm(self):
        try:
            # Get number of processes and auto-generate process names
            num_processes = int(self.num_processes_entry.get().strip())
            processes = [f"P{i+1}" for i in range(num_processes)]
            
            burst = list(map(int, self.burst_entry.get().split(",")))
            
            # Validate that burst times match number of processes
            if len(burst) != num_processes:
                messagebox.showerror("Error", f"Number of burst times ({len(burst)}) must match number of processes ({num_processes})")
                return
            
            arrival_text = self.arrival_entry.get().strip()
            arrival = list(map(int, arrival_text.split(","))) if arrival_text else [0]*num_processes
            
            # Validate arrival times
            if arrival_text and len(arrival) != num_processes:
                messagebox.showerror("Error", f"Number of arrival times ({len(arrival)}) must match number of processes ({num_processes})")
                return
            
            priority_text = self.priority_entry.get().strip()
            priority = list(map(int, priority_text.split(","))) if priority_text else [0]*num_processes
            
            # Validate priority values
            if priority_text and len(priority) != num_processes:
                messagebox.showerror("Error", f"Number of priority values ({len(priority)}) must match number of processes ({num_processes})")
                return
            
            quantum_text = self.quantum_entry.get().strip()
            quantum = int(quantum_text) if quantum_text else 2

            algo = self.selected_algo.get()
            if algo == "FCFS":
                st, ct, wt, tat = fcfs(processes, arrival, burst)
            elif algo == "SJF with AT":
                st, ct, wt, tat = sjf_with_at(processes, arrival, burst)
            elif algo == "SJF without AT":
                st, ct, wt, tat = sjf_without_at(processes, burst)
            elif algo == "Priority Scheduling":
                st, ct, wt, tat = priority_scheduling(processes, arrival, burst, priority)
            elif algo == "Round Robin":
                st, ct, wt, tat = round_robin(processes, arrival, burst, quantum)
            else:
                messagebox.showerror("Error", "Unknown Algorithm")
                return

            avg_tat = sum(tat)/len(tat)
            avg_wt = sum(wt)/len(wt)
            
            # Calculate throughput (processes per unit time)
            total_time = max(ct)
            throughput = len(processes) / total_time if total_time > 0 else 0

            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, f"\n{'='*110}\n")
            self.output_text.insert(tk.END, f"{'SCHEDULING RESULTS':^110}\n")
            self.output_text.insert(tk.END, f"{'='*110}\n\n")
            self.output_text.insert(tk.END, f"{'Process':<12}{'Arrival':<12}{'Burst':<12}{'Start':<12}{'Completion':<15}{'Waiting':<12}{'Turnaround':<12}\n")
            self.output_text.insert(tk.END, "-"*110 + "\n")
            for i in range(len(processes)):
                self.output_text.insert(tk.END, f"{processes[i]:<12}{arrival[i]:<12}{burst[i]:<12}{st[i]:<12}{ct[i]:<15}{wt[i]:<12}{tat[i]:<12}\n")
            self.output_text.insert(tk.END, "-"*110 + "\n\n")
            self.output_text.insert(tk.END, f"{'PERFORMANCE METRICS':^110}\n")
            self.output_text.insert(tk.END, f"{'-'*110}\n")
            self.output_text.insert(tk.END, f"  Average Turnaround Time: {avg_tat:.2f}\n")
            self.output_text.insert(tk.END, f"  Average Waiting Time: {avg_wt:.2f}\n")
            self.output_text.insert(tk.END, f"  Throughput: {throughput:.4f} processes/unit time\n")
            self.output_text.insert(tk.END, f"{'='*110}\n")

        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def toggle_theme(self):
        """Toggle between dark and light themes"""
        self.is_dark_mode = not self.is_dark_mode
        theme = self.themes['dark'] if self.is_dark_mode else self.themes['light']
        
        # Update root background
        self.root.configure(bg=theme['bg'])
        
        # Update main frame
        self.main_frame.configure(bg=theme['bg'])
        
        # Update title and theme button
        self.title_label.configure(bg=theme['bg'], fg=theme['title_fg'])
        self.theme_button.configure(
            text="☀️ Light Mode" if self.is_dark_mode else "🌙 Dark Mode",
            bg=theme['button_bg'], 
            fg=theme['button_fg']
        )
        title_frame = self.theme_button.master
        title_frame.configure(bg=theme['bg'])
        
        # Update all labels
        for label in [self.algo_label, self.num_label, self.burst_label, 
                      self.arrival_label, self.priority_label, self.quantum_label]:
            label.configure(bg=theme['bg'], fg=theme['fg'])
        
        # Update all entry fields
        for entry in [self.num_processes_entry, self.burst_entry, self.arrival_entry, 
                      self.priority_entry, self.quantum_entry]:
            entry.configure(bg=theme['entry_bg'], fg=theme['entry_fg'])
        
        # Update run button
        self.run_button.configure(bg=theme['button_bg'], fg=theme['button_fg'])
        
        # Update output text area
        self.output_text.configure(bg=theme['output_bg'], fg=theme['output_fg'])

if __name__ == "__main__":
    root = tk.Tk()
    app = CPUSchedulingApp(root)
    root.mainloop()