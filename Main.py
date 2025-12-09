import os
import sys
import time
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import psutil
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle  # <--- Added missing import
from cryptography.fernet import Fernet
import pyperclip

# Check for pyudev availability
try:
    import pyudev
    PYUDEV_AVAILABLE = True
except ImportError:
    PYUDEV_AVAILABLE = False


class MainMenuApp:
    """Main landing page with all project options"""
    def __init__(self, root):
        self.root = root
        self.root.title("Linux Security Suite - Main Menu")
        self.root.geometry("900x700")
        
        # Theme configuration
        self.is_dark_mode = True
        self.themes = {
            'dark': {
                'bg': '#2E3440',
                'fg': '#D8DEE9',
                'title_fg': '#88C0D0',
                'card_bg': '#3B4252',
                'button_bg': '#81A1C1',
                'button_fg': 'black',
                'accent': '#5E81AC'
            },
            'light': {
                'bg': '#F5F5F5',
                'fg': '#2E3440',
                'title_fg': '#0066CC',
                'card_bg': '#FFFFFF',
                'button_bg': '#4A90E2',
                'button_fg': 'white',
                'accent': '#0066CC'
            }
        }
        
        self.apply_theme()
        self.create_main_menu()
    
    def apply_theme(self):
        theme = self.themes['dark'] if self.is_dark_mode else self.themes['light']
        self.root.configure(bg=theme['bg'])
    
    def create_main_menu(self):
        theme = self.themes['dark'] if self.is_dark_mode else self.themes['light']
        
        # Main container
        main_frame = tk.Frame(self.root, bg=theme['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header with title and theme toggle
        header_frame = tk.Frame(main_frame, bg=theme['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 30))
        
        title_label = tk.Label(header_frame, text="🐧 Linux Security Suite", 
                               font=("Arial", 32, "bold"), 
                               bg=theme['bg'], fg=theme['title_fg'])
        title_label.pack(side=tk.LEFT)
        
        theme_btn = tk.Button(header_frame, 
                             text="☀️ Light" if self.is_dark_mode else "🌙 Dark",
                             command=self.toggle_theme,
                             bg=theme['button_bg'], fg=theme['button_fg'],
                             font=("Arial", 12, "bold"), padx=15, pady=8, cursor="hand2")
        theme_btn.pack(side=tk.RIGHT)
        
        subtitle = tk.Label(main_frame, 
                           text="Comprehensive System Management & Security Tools",
                           font=("Arial", 14), bg=theme['bg'], fg=theme['fg'])
        subtitle.pack(pady=(0, 40))
        
        # Projects grid
        projects_frame = tk.Frame(main_frame, bg=theme['bg'])
        projects_frame.pack(fill=tk.BOTH, expand=True)
        
        projects = [
            ("💻 CPU Scheduling", "Simulate CPU scheduling algorithms (FCFS, SJF, Priority, RR)", self.open_cpu_scheduling),
            ("📁 File Manager", "Browse, create, edit, and manage files", self.open_file_manager),
            ("📊 System Monitor", "Real-time CPU and RAM usage monitoring", self.open_system_monitor),
            ("🌐 Network Monitor", "Track network connections and traffic", self.open_network_monitor),
            ("🔐 Encryption Tool", "Encrypt and decrypt messages securely", self.open_encryption_tool),
            ("🔌 USB Monitor", "Monitor connected USB devices (Linux only)", self.open_usb_monitor),
        ]
        
        for idx, (title, desc, command) in enumerate(projects):
            row = idx // 2
            col = idx % 2
            
            card = tk.Frame(projects_frame, bg=theme['card_bg'], relief=tk.RAISED, borderwidth=2)
            card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
            
            card_title = tk.Label(card, text=title, font=("Arial", 16, "bold"),
                                 bg=theme['card_bg'], fg=theme['accent'])
            card_title.pack(pady=(15, 5))
            
            card_desc = tk.Label(card, text=desc, font=("Arial", 11),
                                bg=theme['card_bg'], fg=theme['fg'], wraplength=300)
            card_desc.pack(pady=(0, 10))
            
            open_btn = tk.Button(card, text="Open →", command=command,
                                bg=theme['button_bg'], fg=theme['button_fg'],
                                font=("Arial", 12, "bold"), padx=20, pady=8, cursor="hand2")
            open_btn.pack(pady=(5, 15))
        
        # Configure grid weights
        for i in range(3):
            projects_frame.grid_rowconfigure(i, weight=1)
        for i in range(2):
            projects_frame.grid_columnconfigure(i, weight=1)
    
    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        # Clear and recreate
        for widget in self.root.winfo_children():
            widget.destroy()
        self.apply_theme()
        self.create_main_menu()
    
    def open_cpu_scheduling(self):
        new_window = tk.Toplevel(self.root)
        CPUSchedulingApp(new_window)
    
    def open_file_manager(self):
        new_window = tk.Toplevel(self.root)
        FileManagerApp(new_window)
    
    def open_system_monitor(self):
        new_window = tk.Toplevel(self.root)
        ResourceMonitorApp(new_window)
    
    def open_network_monitor(self):
        new_window = tk.Toplevel(self.root)
        NetworkMonitorApp(new_window)
    
    def open_encryption_tool(self):
        new_window = tk.Toplevel(self.root)
        SimpleEncryptionDecryptionTool(new_window)
    
    def open_usb_monitor(self):
        if not PYUDEV_AVAILABLE:
            messagebox.showwarning("Module Missing", 
                                 "pyudev module is not installed. Install it with:\npip install pyudev")
            return
        new_window = tk.Toplevel(self.root)
        USBMonitorApp(new_window)


# ==================== CPU SCHEDULING APP ====================
# ==================== CPU SCHEDULING APP (UPDATED WITH SCROLLING) ====================
class CPUSchedulingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CPU Scheduling Algorithms")
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
        self.create_widgets()
        
        # Bind mouse wheel scrolling
        self._bind_mouse_scroll()

    def create_widgets(self):
        theme = self.themes['dark'] if self.is_dark_mode else self.themes['light']
        
        # Scrollable canvas for longer content
        self.main_canvas = tk.Canvas(self.root, bg=theme['bg']) # Made class variable
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.main_canvas.yview)
        scrollable_frame = tk.Frame(self.main_canvas, bg=theme['bg'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )
        
        self.main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        self.main_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Main frame inside scrollable area
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

        # Internal scrollbar for text box
        self.text_scrollbar = tk.Scrollbar(self.main_frame, command=self.output_text.yview)
        self.text_scrollbar.grid(row=8, column=2, sticky="ns", pady=20)
        self.output_text.config(yscrollcommand=self.text_scrollbar.set)

        # Gantt Chart Frame
        self.gantt_frame = tk.Frame(self.main_frame, bg=theme['bg'])
        self.gantt_frame.grid(row=9, column=0, columnspan=2, pady=20)
        
        gantt_title = tk.Label(self.gantt_frame, text="📊 Gantt Chart Visualization", 
                              bg=theme['bg'], fg=theme['title_fg'], font=("Arial", 18, "bold"))
        gantt_title.pack(pady=10)

    def _bind_mouse_scroll(self):
        # Bind events to the root window (this Toplevel window)
        self.root.bind("<MouseWheel>", self._on_mousewheel)  # Windows
        self.root.bind("<Button-4>", self._on_linux_scroll_up)  # Linux scroll up
        self.root.bind("<Button-5>", self._on_linux_scroll_down)  # Linux scroll down

    def _on_mousewheel(self, event):
        # Windows/MacOS scroll event
        self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _on_linux_scroll_up(self, event):
        self.main_canvas.yview_scroll(-1, "units")

    def _on_linux_scroll_down(self, event):
        self.main_canvas.yview_scroll(1, "units")

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
        """
        Draws a Gantt chart showing process execution timeline
        """
        # Clear previous chart (keep only the title label)
        for widget in self.gantt_frame.winfo_children():
            if not isinstance(widget, tk.Label):
                widget.destroy()
        
        theme = self.themes['dark'] if self.is_dark_mode else self.themes['light']
        
        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(12, 4))
        fig.patch.set_facecolor(theme['bg'])
        ax.set_facecolor(theme['output_bg'])
        
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
                     color=theme['fg'])
        ax.set_yticks([])
        ax.set_title('Process Execution Timeline (Gantt Chart)', fontsize=14, fontweight='bold',
                    color=theme['title_fg'], pad=20)
        
        # Style the axes
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.tick_params(colors=theme['fg'])
        
        # Add time markers
        time_points = sorted(set([0] + start_times + completion_times))
        ax.set_xticks(time_points)
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.gantt_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10)

    # --- ALGORITHMS ---
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
# ==================== FILE MANAGER APP ====================
class FileManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Linux File Manager")
        self.root.geometry("700x700")
        self.root.configure(bg="#f0f0f0")

        self.title_label = tk.Label(self.root, text="Linux File Manager", font=("Arial", 20, "bold"), bg="#f0f0f0")
        self.title_label.pack(pady=20)

        self.dir_path_label = tk.Label(self.root, text="Current Directory: ", font=("Arial", 12), bg="#f0f0f0")
        self.dir_path_label.pack()

        self.current_dir = tk.StringVar()
        self.current_dir.set(os.getcwd())
        self.current_dir_label = tk.Label(self.root, textvariable=self.current_dir, font=("Arial", 12, "italic"), bg="#f0f0f0", fg="#0066cc")
        self.current_dir_label.pack(pady=5)

        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(pady=10)

        self.file_listbox = tk.Listbox(frame, height=15, width=50, font=("Arial", 12), bd=0, selectmode=tk.SINGLE, bg="#ffffff", fg="#333333", relief="sunken")
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(frame, orient="vertical", command=self.file_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_listbox.config(yscrollcommand=scrollbar.set)

        button_frame = tk.Frame(self.root, bg="#f0f0f0")
        button_frame.pack(pady=20)

        self.refresh_button = tk.Button(button_frame, text="Refresh", command=self.refresh_directory, width=15, height=2, font=("Arial", 12), bg="#4CAF50", fg="white", relief="raised", bd=2)
        self.refresh_button.grid(row=0, column=0, padx=10, pady=5)

        self.change_dir_button = tk.Button(button_frame, text="Change Directory", command=self.change_directory, width=15, height=2, font=("Arial", 12), bg="#2196F3", fg="white", relief="raised", bd=2)
        self.change_dir_button.grid(row=0, column=1, padx=10, pady=5)

        self.create_file_button = tk.Button(button_frame, text="Create File", command=self.create_file, width=15, height=2, font=("Arial", 12), bg="#FFC107", fg="white", relief="raised", bd=2)
        self.create_file_button.grid(row=1, column=0, padx=10, pady=5)

        self.delete_file_button = tk.Button(button_frame, text="Delete File", command=self.delete_file, width=15, height=2, font=("Arial", 12), bg="#F44336", fg="white", relief="raised", bd=2)
        self.delete_file_button.grid(row=1, column=1, padx=10, pady=5)

        self.write_to_file_button = tk.Button(button_frame, text="Write to File", command=self.write_to_file, width=15, height=2, font=("Arial", 12), bg="#9C27B0", fg="white", relief="raised", bd=2)
        self.write_to_file_button.grid(row=2, column=0, padx=10, pady=5)

        self.view_file_button = tk.Button(button_frame, text="View File", command=self.view_file, width=15, height=2, font=("Arial", 12), bg="#607D8B", fg="white", relief="raised", bd=2)
        self.view_file_button.grid(row=2, column=1, padx=10, pady=5)

        self.refresh_directory()

    def refresh_directory(self):
        self.file_listbox.delete(0, tk.END)
        try:
            for file in os.listdir(self.current_dir.get()):
                self.file_listbox.insert(tk.END, file)
        except Exception as e:
            messagebox.showerror("Error", f"Could not refresh directory: {e}")

    def change_directory(self):
        new_dir = filedialog.askdirectory(initialdir=self.current_dir.get(), title="Select a Directory")
        if new_dir:
            self.current_dir.set(new_dir)
            self.refresh_directory()

    def create_file(self):
        file_name = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_name:
            try:
                with open(file_name, 'w') as f:
                    f.write("") 
                self.refresh_directory()
            except Exception as e:
                messagebox.showerror("Error", f"Could not create file: {e}")

    def delete_file(self):
        selected_file = self.file_listbox.curselection()
        if selected_file:
            file_name = self.file_listbox.get(selected_file)
            file_path = os.path.join(self.current_dir.get(), file_name)
            confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {file_name}?")
            if confirm:
                try:
                    os.remove(file_path)
                    self.refresh_directory()
                except Exception as e:
                    messagebox.showerror("Error", f"Could not delete file: {e}")
        else:
            messagebox.showwarning("No Selection", "Please select a file to delete.")

    def write_to_file(self):
        selected_file = self.file_listbox.curselection()
        if selected_file:
            file_name = self.file_listbox.get(selected_file)
            file_path = os.path.join(self.current_dir.get(), file_name)
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                write_window = tk.Toplevel(self.root)
                write_window.title(f"Write to {file_name}")
                write_window.geometry("600x400")

                text_box = tk.Text(write_window, height=15, width=70, font=("Arial", 12), wrap=tk.WORD)
                text_box.pack(padx=10, pady=10)
                text_box.insert(tk.END, content)

                def save_changes():
                    updated_content = text_box.get("1.0", tk.END).strip()
                    with open(file_path, 'w') as f:
                        f.write(updated_content)
                    messagebox.showinfo("Success", f"Changes saved to {file_name}")
                    write_window.destroy()
                    self.refresh_directory()

                save_button = tk.Button(write_window, text="Save Changes", command=save_changes, width=15, height=2, font=("Arial", 12), bg="#4CAF50", fg="white", relief="raised", bd=2)
                save_button.pack(pady=10)

            except Exception as e:
                messagebox.showerror("Error", f"Could not open file for writing: {e}")
        else:
            messagebox.showwarning("No Selection", "Please select a file to write to.")

    def view_file(self):
        selected_file = self.file_listbox.curselection()
        if selected_file:
            file_name = self.file_listbox.get(selected_file)
            file_path = os.path.join(self.current_dir.get(), file_name)
            try:
                with open(file_path, 'r') as f:
                    content = f.read()

                view_window = tk.Toplevel(self.root)
                view_window.title(f"View: {file_name}")
                view_window.geometry("600x400")

                text_box = tk.Text(view_window, height=15, width=70, font=("Arial", 12), wrap=tk.WORD)
                text_box.pack(padx=10, pady=10)
                text_box.insert(tk.END, content)
                text_box.config(state=tk.DISABLED) 
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")
        else:
            messagebox.showwarning("No Selection", "Please select a file to view.")


# ==================== RESOURCE MONITOR APP ====================
class ResourceMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Linux Security Suite - Resource Monitor")
        self.root.geometry("900x600")

        sns.set_style("darkgrid")

        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 8))
        plt.subplots_adjust(hspace=0.5)

        self.x_data = []
        self.cpu_data = []
        self.ram_data = []

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.ani = FuncAnimation(self.fig, self.update, interval=1000, cache_frame_data=False)

    def update(self, frame):
        current_time = time.strftime("%H:%M:%S")
        self.x_data.append(current_time)

        cpu = psutil.cpu_percent(interval=0.1)
        self.cpu_data.append(cpu)
        self.ax1.clear()
        self.ax1.plot(self.x_data, self.cpu_data, label="CPU Usage", color="blue")
        self.ax1.set_title("CPU Usage (%)")
        self.ax1.set_xlabel("Time")
        self.ax1.set_ylabel("Usage (%)")
        self.ax1.legend(loc="upper left")
        self.ax1.grid(True)
        self.ax1.tick_params(axis='x', rotation=45)
        self.ax1.set_xticks(self.x_data[::5])
        self.ax1.text(0.95, 0.95, f"{cpu:.1f}%", transform=self.ax1.transAxes,
             fontsize=12, verticalalignment='top', horizontalalignment='right', color="blue")

        ram = psutil.virtual_memory().percent
        self.ram_data.append(ram)
        self.ax2.clear()
        self.ax2.plot(self.x_data, self.ram_data, label="RAM Usage", color="green")
        self.ax2.set_title("RAM Usage (%)")
        self.ax2.set_xlabel("Time")
        self.ax2.set_ylabel("Usage (%)")
        self.ax2.legend(loc="upper left")
        self.ax2.grid(True)
        self.ax2.tick_params(axis='x', rotation=45)
        self.ax2.set_xticks(self.x_data[::5])
        self.ax2.text(0.95, 0.95, f"{ram:.1f}%", transform=self.ax2.transAxes,
             fontsize=12, verticalalignment='top', horizontalalignment='right', color="green")

        if len(self.x_data) > 30:
            self.x_data.pop(0)
            self.cpu_data.pop(0)
            self.ram_data.pop(0)

        self.canvas.draw()


# ==================== NETWORK MONITOR APP ====================
class NetworkMonitorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Network Monitor")
        self.master.geometry("900x700")

        self.create_network_monitor(master)

        self.net_data = {'sent': [], 'recv': []}
        self.last_net_io = psutil.net_io_counters()
        self.timestamps = []

        self.ani = FuncAnimation(self.ax_net.figure, self.update_network_info, interval=1000, save_count=50)
        self.ani._start() 

    def create_network_monitor(self, parent):
        panel = ttk.LabelFrame(parent, text="Network Activity", padding=10)
        panel.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.connection_tree = ttk.Treeview(panel, columns=('Proto', 'Local', 'Remote', 'Status', 'PID'), show='headings')
        
        self.connection_tree.heading('Proto', text='Protocol')
        self.connection_tree.heading('Local', text='Local Address')
        self.connection_tree.heading('Remote', text='Remote Address')
        self.connection_tree.heading('Status', text='Status')
        self.connection_tree.heading('PID', text='PID')
        
        self.connection_tree.column('Proto', width=60)
        self.connection_tree.column('Local', width=150)
        self.connection_tree.column('Remote', width=150)
        self.connection_tree.column('Status', width=80)
        self.connection_tree.column('PID', width=50)
        
        scrollbar = ttk.Scrollbar(panel, orient=tk.VERTICAL, command=self.connection_tree.yview)
        self.connection_tree.configure(yscroll=scrollbar.set)
        
        self.connection_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        fig, self.ax_net = plt.subplots(figsize=(6, 3), dpi=100)
        self.ax_net.set_title("Network Traffic", fontsize=12, fontweight='bold')
        self.ax_net.set_ylabel("KB/s", fontsize=10)
        self.ax_net.grid(True, linestyle='--', alpha=0.6)
        
        self.canvas_net = FigureCanvasTkAgg(fig, master=panel)
        self.canvas_net.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=5)

    def update_network_info(self, frame=None):
        self.update_connection_info()
        self.update_network_traffic_graph()

    def update_connection_info(self):
        for item in self.connection_tree.get_children():
            self.connection_tree.delete(item)
        
        try:
            connections = psutil.net_connections()
            for conn in connections:
                if conn.status == 'LISTEN':
                    continue 
                
                laddr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else ""
                raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else ""
                
                self.connection_tree.insert('', 'end', 
                                          values=(conn.type.name, 
                                                  laddr, 
                                                  raddr, 
                                                  conn.status, 
                                                  conn.pid or "N/A"))
        except (psutil.AccessDenied, PermissionError):
            self.connection_tree.insert('', 'end', values=("Access", "denied", "", "", ""))

    def update_network_traffic_graph(self):
        current_net_io = psutil.net_io_counters()
        elapsed = 1 
        
        sent_kb = (current_net_io.bytes_sent - self.last_net_io.bytes_sent) / 1024 / elapsed
        recv_kb = (current_net_io.bytes_recv - self.last_net_io.bytes_recv) / 1024 / elapsed

        self.net_data['sent'].append(sent_kb)
        self.net_data['recv'].append(recv_kb)
        self.timestamps.append(time.strftime("%H:%M:%S"))

        if len(self.net_data['sent']) > 30:
            self.net_data['sent'].pop(0)
            self.net_data['recv'].pop(0)
            self.timestamps.pop(0)

        self.ax_net.clear()
        self.ax_net.plot(self.timestamps, self.net_data['sent'], label="Sent", color='blue', linewidth=1.5)
        self.ax_net.plot(self.timestamps, self.net_data['recv'], label="Received", color='green', linewidth=1.5)

        self.ax_net.set_title(f"Network Traffic (Sent: {sent_kb:.1f} KB/s, Recv: {recv_kb:.1f} KB/s)", fontsize=12, fontweight='bold')
        self.ax_net.set_ylabel("KB/s", fontsize=10)
        self.ax_net.set_xlabel("Time", fontsize=10)
        self.ax_net.legend(loc='upper right', fontsize=9)
        self.ax_net.grid(True, linestyle='--', alpha=0.6)

        self.ax_net.set_xticks(range(0, len(self.timestamps), max(1, len(self.timestamps) // 10)))
        self.ax_net.set_xticklabels(self.timestamps[::max(1, len(self.timestamps) // 10)], rotation=30, ha='right')

        self.canvas_net.draw()

        self.last_net_io = current_net_io


# ==================== ENCRYPTION TOOL ====================
class SimpleEncryptionDecryptionTool:
    def __init__(self, master):
        self.master = master
        self.master.title("Encryption & Decryption Tool")
        self.master.geometry("600x500")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=('Segoe UI', 10), padding=6)
        style.configure("TLabel", font=('Segoe UI', 11))

        self.encryption_frame = ttk.LabelFrame(master, text="🔐 Encryption", padding=15)
        self.encryption_frame.pack(padx=10, pady=10, fill='x')

        ttk.Label(self.encryption_frame, text="Encryption Key:").grid(row=0, column=0, sticky='w')
        self.key_entry = ttk.Entry(self.encryption_frame, width=50)
        self.key_entry.grid(row=0, column=1, pady=5)

        ttk.Button(self.encryption_frame, text="Generate Key", command=self.generate_key).grid(row=1, column=1, sticky='w')
        ttk.Button(self.encryption_frame, text="Copy Key", command=self.copy_key_to_clipboard).grid(row=1, column=1, sticky='e')

        ttk.Label(self.encryption_frame, text="Enter Message:").grid(row=2, column=0, sticky='w')
        self.message_entry = ttk.Entry(self.encryption_frame, width=50)
        self.message_entry.grid(row=2, column=1, pady=5)

        ttk.Button(self.encryption_frame, text="Encrypt", command=self.encrypt_message).grid(row=3, column=1, sticky='w', pady=5)

        self.encrypted_message_display = ttk.Label(self.encryption_frame, text="", foreground="green")
        self.encrypted_message_display.grid(row=4, column=0, columnspan=2, pady=5)

        ttk.Button(self.encryption_frame, text="Copy Encrypted", command=self.copy_encrypted_message).grid(row=5, column=1, sticky='e')

        self.decryption_frame = ttk.LabelFrame(master, text="🔓 Decryption", padding=15)
        self.decryption_frame.pack(padx=10, pady=10, fill='x')

        ttk.Label(self.decryption_frame, text="Encryption Key:").grid(row=0, column=0, sticky='w')
        self.decrypted_key_entry = ttk.Entry(self.decryption_frame, width=50)
        self.decrypted_key_entry.grid(row=0, column=1, pady=5)

        ttk.Label(self.decryption_frame, text="Encrypted Message:").grid(row=1, column=0, sticky='w')
        self.decrypted_message_entry = ttk.Entry(self.decryption_frame, width=50)
        self.decrypted_message_entry.grid(row=1, column=1, pady=5)

        ttk.Button(self.decryption_frame, text="Decrypt", command=self.decrypt_message).grid(row=2, column=1, sticky='w', pady=5)

        self.decrypted_message_result = ttk.Label(self.decryption_frame, text="", foreground="blue")
        self.decrypted_message_result.grid(row=3, column=0, columnspan=2, pady=5)

    def generate_key(self):
        key = Fernet.generate_key()
        self.key_entry.delete(0, tk.END)
        self.key_entry.insert(0, key.decode())

    def encrypt_message(self):
        message = self.message_entry.get()
        key = self.key_entry.get().encode()

        if not message:
            messagebox.showwarning("Missing Message", "Please enter a message to encrypt.")
            return
        if not key:
            messagebox.showwarning("Missing Key", "Please generate or enter an encryption key.")
            return

        try:
            cipher = Fernet(key)
            encrypted = cipher.encrypt(message.encode()).decode()
            self.encrypted_message_display.config(text=f"{encrypted}")
        except Exception as e:
            self.encrypted_message_display.config(text="Invalid Key!")

    def decrypt_message(self):
        encrypted_message = self.decrypted_message_entry.get()
        key = self.decrypted_key_entry.get().encode()

        if not encrypted_message:
            messagebox.showwarning("Missing Encrypted Message", "Please enter the encrypted message.")
            return
        if not key:
            messagebox.showwarning("Missing Key", "Please enter the encryption key.")
            return

        try:
            cipher = Fernet(key)
            decrypted = cipher.decrypt(encrypted_message.encode()).decode()
            self.decrypted_message_result.config(text=f"Decrypted: {decrypted}")
        except Exception:
            self.decrypted_message_result.config(text="Invalid key or message!")

    def copy_key_to_clipboard(self):
        key = self.key_entry.get()
        if key:
            pyperclip.copy(key)
            messagebox.showinfo("Copied", "Encryption key copied to clipboard!")

    def copy_encrypted_message(self):
        encrypted_message = self.encrypted_message_display.cget("text")
        if encrypted_message:
            pyperclip.copy(encrypted_message)
            messagebox.showinfo("Copied", "Encrypted message copied to clipboard!")


# ==================== USB MONITOR APP ====================
class USBMonitorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("USB Device Monitor")
        self.master.geometry("900x600")

        self.create_ui()
        self.monitor_usb_devices()
        if PYUDEV_AVAILABLE:
            self.start_usb_event_listener()
    
    def create_ui(self):
        self.usb_frame = ttk.LabelFrame(self.master, text="🔌 Connected USB Devices")
        self.usb_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.usb_tree = ttk.Treeview(self.usb_frame, columns=("Bus", "Device", "ID", "Details"), show="headings", height=12)
        for col in ("Bus", "Device", "ID", "Details"):
            self.usb_tree.heading(col, text=col)
            self.usb_tree.column(col, width=150 if col != "Details" else 400)
        self.usb_tree.pack(fill=tk.BOTH, expand=True)
        
        button_frame = ttk.Frame(self.master)
        button_frame.pack(pady=5)
        
        self.refresh_button = ttk.Button(button_frame, text="🔄 Refresh USB Devices", command=self.monitor_usb_devices)
        self.refresh_button.grid(row=0, column=0, padx=5)
        
        self.details_button = ttk.Button(button_frame, text="🔍 Show Device Details", command=self.show_device_details)
        self.details_button.grid(row=0, column=1, padx=5)
        
        self.details_label = ttk.Label(self.master, text="Device details will appear here...", wraplength=750, justify="left")
        self.details_label.pack(pady=10)

    def monitor_usb_devices(self):
        self.usb_tree.delete(*self.usb_tree.get_children())
        try:
            result = subprocess.run(["lsusb"], check=True, text=True, capture_output=True)
            for line in result.stdout.splitlines():
                parts = line.split()
                if len(parts) < 6:
                    continue  
                bus, device, usb_id = parts[1], parts[3][:-1], parts[5]
                details = " ".join(parts[6:])
                self.usb_tree.insert("", tk.END, values=(bus, device, usb_id, details))
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to fetch USB devices:\n{e}")
        except FileNotFoundError:
            messagebox.showerror("Error", "lsusb command not found. This feature requires Linux.")

    def show_device_details(self):
        selected_item = self.usb_tree.selection()
        if not selected_item:
            self.details_label.config(text="⚠️ Please select a device to view details.")
            return

        device_info = self.usb_tree.item(selected_item, "values")
        bus, device = device_info[0], device_info[1]
        
        bus = bus.zfill(3)
        device = device.zfill(3)
        device_path = f"/dev/bus/usb/{bus}/{device}"

        try:
            result = subprocess.run(["udevadm", "info", "--query=all", "--name=" + device_path],
                                    check=True, text=True, capture_output=True)
            output = result.stdout.strip()
            self.details_label.config(text=(output[:500] + "...") if len(output) > 500 else output)
        except subprocess.CalledProcessError as e:
            self.details_label.config(text=f"❌ Error fetching details:\n{e}")
        except FileNotFoundError:
            self.details_label.config(text="❌ udevadm command not found.")

    def start_usb_event_listener(self):
        threading.Thread(target=self.usb_event_listener, daemon=True).start()

    def usb_event_listener(self):
        try:
            context = pyudev.Context()
            monitor = pyudev.Monitor.from_netlink(context)
            monitor.filter_by(subsystem='usb')
            for device in iter(monitor.poll, None):
                self.monitor_usb_devices()
        except Exception as e:
            print(f"USB event listener error: {e}")


# ==================== MAIN PROGRAM ====================
if __name__ == "__main__":
    root = tk.Tk()
    app = MainMenuApp(root)
    root.mainloop()