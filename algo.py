import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Rectangle
import random

class CPUSchedulingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CPU Scheduling Algorithms with Gantt Chart")
        self.root.geometry("1200x950")
        
        self.algorithms = ["FCFS", "SJF with AT", "SJF without AT", "Priority Scheduling", "Round Robin"]
        self.selected_algo = tk.StringVar(value=self.algorithms[0])
        
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
        self.gantt_data = []
        self.create_widgets()

    def create_widgets(self):
        theme = self.themes['dark'] if self.is_dark_mode else self.themes['light']
        
        # Main container with scrollbar
        main_canvas = tk.Canvas(self.root, bg=theme['bg'])
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas, bg=theme['bg'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.main_frame = tk.Frame(scrollable_frame, bg=theme['bg'])
        self.main_frame.pack(padx=20, pady=20)

        label_style = {"bg": theme['bg'], "fg": theme['fg'], "font":("Arial", 14, "bold")}
        entry_style = {"width":50, "font":("Arial", 12), "bg": theme['entry_bg'], "fg": theme['entry_fg']}

        title_frame = tk.Frame(self.main_frame, bg=theme['bg'])
        title_frame.grid(row=0, column=0, columnspan=2, pady=30)
        
        self.title_label = tk.Label(title_frame, text="CPU Scheduling Algorithms", 
                               bg=theme['bg'], fg=theme['title_fg'], font=("Arial", 24, "bold"))
        self.title_label.pack(side="left", padx=(0, 20))

        self.algo_label = tk.Label(self.main_frame, text="Select Algorithm:", **label_style)
        self.algo_label.grid(row=1, column=0, padx=10, pady=15, sticky="e")
        self.algo_menu = ttk.Combobox(self.main_frame, values=self.algorithms, textvariable=self.selected_algo, 
                                      width=48, font=("Arial", 12))
        self.algo_menu.grid(row=1, column=1, padx=10, pady=15, sticky="w")

        self.num_label = tk.Label(self.main_frame, text="Number of Processes:", **label_style)
        self.num_label.grid(row=2, column=0, padx=10, pady=15, sticky="e")
        self.num_processes_entry = tk.Entry(self.main_frame, **entry_style)
        self.num_processes_entry.grid(row=2, column=1, padx=10, pady=15, sticky="w")

        self.burst_label = tk.Label(self.main_frame, text="Burst Times (e.g., 5,3,8):", **label_style)
        self.burst_label.grid(row=3, column=0, padx=10, pady=15, sticky="e")
        self.burst_entry = tk.Entry(self.main_frame, **entry_style)
        self.burst_entry.grid(row=3, column=1, padx=10, pady=15, sticky="w")

        self.arrival_label = tk.Label(self.main_frame, text="Arrival Times (optional):", **label_style)
        self.arrival_label.grid(row=4, column=0, padx=10, pady=15, sticky="e")
        self.arrival_entry = tk.Entry(self.main_frame, **entry_style)
        self.arrival_entry.grid(row=4, column=1, padx=10, pady=15, sticky="w")

        self.priority_label = tk.Label(self.main_frame, text="Priority (for Priority Scheduling):", **label_style)
        self.priority_label.grid(row=5, column=0, padx=10, pady=15, sticky="e")
        self.priority_entry = tk.Entry(self.main_frame, **entry_style)
        self.priority_entry.grid(row=5, column=1, padx=10, pady=15, sticky="w")

        self.quantum_label = tk.Label(self.main_frame, text="Time Quantum (for Round Robin):", **label_style)
        self.quantum_label.grid(row=6, column=0, padx=10, pady=15, sticky="e")
        self.quantum_entry = tk.Entry(self.main_frame, **entry_style)
        self.quantum_entry.grid(row=6, column=1, padx=10, pady=15, sticky="w")

        self.run_button = tk.Button(self.main_frame, text="Run Algorithm", bg=theme['button_bg'], fg=theme['button_fg'], 
                                    font=("Arial", 16, "bold"), command=self.run_algorithm, 
                                    padx=40, pady=15, cursor="hand2")
        self.run_button.grid(row=7, column=0, columnspan=2, pady=30)

        self.output_text = tk.Text(self.main_frame, height=15, width=110, bg=theme['output_bg'], fg=theme['output_fg'], 
                                   font=("Courier", 11), relief="solid", borderwidth=2)
        self.output_text.grid(row=8, column=0, columnspan=2, padx=10, pady=20)

        # Gantt Chart Frame
        self.gantt_frame = tk.Frame(self.main_frame, bg=theme['bg'])
        self.gantt_frame.grid(row=9, column=0, columnspan=2, pady=20)
        
        gantt_title = tk.Label(self.gantt_frame, text="Gantt Chart Visualization", 
                              bg=theme['bg'], fg=theme['title_fg'], font=("Arial", 18, "bold"))
        gantt_title.pack(pady=10)

    def run_algorithm(self):
        try:
            num_processes = int(self.num_processes_entry.get().strip())
            processes = [f"P{i+1}" for i in range(num_processes)]
            
            burst = list(map(int, self.burst_entry.get().split(",")))
            
            if len(burst) != num_processes:
                messagebox.showerror("Error", f"Number of burst times ({len(burst)}) must match number of processes ({num_processes})")
                return
            
            arrival_text = self.arrival_entry.get().strip()
            arrival = list(map(int, arrival_text.split(","))) if arrival_text else [0]*num_processes
            
            if arrival_text and len(arrival) != num_processes:
                messagebox.showerror("Error", f"Number of arrival times ({len(arrival)}) must match number of processes ({num_processes})")
                return
            
            priority_text = self.priority_entry.get().strip()
            priority = list(map(int, priority_text.split(","))) if priority_text else [0]*num_processes
            
            if priority_text and len(priority) != num_processes:
                messagebox.showerror("Error", f"Number of priority values ({len(priority)}) must match number of processes ({num_processes})")
                return
            
            quantum_text = self.quantum_entry.get().strip()
            quantum = int(quantum_text) if quantum_text else 2

            algo = self.selected_algo.get()
            if algo == "FCFS":
                st, ct, wt, tat = self.fcfs(processes, arrival, burst)
            elif algo == "SJF with AT":
                st, ct, wt, tat = self.sjf_with_at(processes, arrival, burst)
            elif algo == "SJF without AT":
                st, ct, wt, tat = self.sjf_without_at(processes, burst)
            elif algo == "Priority Scheduling":
                st, ct, wt, tat = self.priority_scheduling(processes, arrival, burst, priority)
            elif algo == "Round Robin":
                st, ct, wt, tat = self.round_robin(processes, arrival, burst, quantum)
            else:
                messagebox.showerror("Error", "Unknown Algorithm")
                return

            avg_tat = sum(tat)/len(tat)
            avg_wt = sum(wt)/len(wt)
            total_time = max(ct)
            throughput = len(processes) / total_time if total_time > 0 else 0

            # Display results
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

            # Draw Gantt Chart
            self.draw_gantt_chart(processes, st, ct)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def draw_gantt_chart(self, processes, start_times, completion_times):
        # Clear previous chart
        for widget in self.gantt_frame.winfo_children():
            if isinstance(widget, tk.Frame) and widget != self.gantt_frame.winfo_children()[0]:
                widget.destroy()
        
        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(12, 4))
        fig.patch.set_facecolor('#2E3440' if self.is_dark_mode else '#F5F5F5')
        ax.set_facecolor('#3B4252' if self.is_dark_mode else '#FFFFFF')
        
        # Generate colors for processes
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', 
                  '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B739', '#52B788']
        
        # Plot each process
        for i, (proc, start, end) in enumerate(zip(processes, start_times, completion_times)):
            duration = end - start
            color = colors[i % len(colors)]
            
            # Draw rectangle for process
            rect = Rectangle((start, 0.4), duration, 0.2, 
                           facecolor=color, edgecolor='black', linewidth=2)
            ax.add_patch(rect)
            
            # Add process label
            ax.text(start + duration/2, 0.5, proc, 
                   ha='center', va='center', fontsize=10, fontweight='bold', color='black')
        
        # Set axis properties
        ax.set_xlim(0, max(completion_times) + 2)
        ax.set_ylim(0, 1)
        ax.set_xlabel('Time', fontsize=12, fontweight='bold', 
                     color='#D8DEE9' if self.is_dark_mode else '#2E3440')
        ax.set_yticks([])
        ax.set_title('Process Execution Timeline (Gantt Chart)', fontsize=14, fontweight='bold',
                    color='#88C0D0' if self.is_dark_mode else '#0066CC', pad=20)
        
        # Style the axes
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.tick_params(colors='#D8DEE9' if self.is_dark_mode else '#2E3440')
        
        # Add time markers
        time_points = sorted(set([0] + start_times + completion_times))
        ax.set_xticks(time_points)
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.gantt_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10)

    def fcfs(self, processes, arrival, burst):
        n = len(processes)
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

    def sjf_with_at(self, processes, arrival, burst):
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

    def sjf_without_at(self, processes, burst):
        n = len(processes)
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

    def priority_scheduling(self, processes, arrival, burst, priority):
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

    def round_robin(self, processes, arrival, burst, quantum):
        n = len(processes)
        remaining = burst.copy()
        current_time = 0
        completion_time = [0]*n
        start_time = [-1]*n
        ready_queue = []
        visited = [False]*n
        
        proc_indices = list(range(n))
        proc_indices.sort(key=lambda x: arrival[x])
        
        i = 0
        while True:
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


if __name__ == "__main__":
    root = tk.Tk()
    app = CPUSchedulingApp(root)
    root.mainloop()