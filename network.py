import tkinter as tk
from tkinter import ttk
import psutil
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import socket

class NetworkMonitorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Network Monitor ⚡")
        self.master.geometry("900x600")

        self.net_data = {'sent': [], 'recv': []}
        self.last_net_io = psutil.net_io_counters()
        self.timestamps = []

        self.create_network_monitor(master)

        # Start animation for live graph (updates every 1 second)
        self.ani = FuncAnimation(self.ax_net.figure, self.update_network_info, interval=1000, blit=False)

    def create_network_monitor(self, parent):
        panel = ttk.LabelFrame(parent, text="Network Activity", padding=10)
        panel.pack(fill=tk.BOTH, expand=True, pady=5)

        self.connection_tree = ttk.Treeview(panel, columns=('Proto', 'Local', 'Remote', 'Status', 'PID'), show='headings')
        for col, width in zip(('Proto', 'Local', 'Remote', 'Status', 'PID'), (60, 200, 200, 80, 50)):
            self.connection_tree.heading(col, text=col)
            self.connection_tree.column(col, width=width)

        scrollbar = ttk.Scrollbar(panel, orient=tk.VERTICAL, command=self.connection_tree.yview)
        self.connection_tree.configure(yscroll=scrollbar.set)
        self.connection_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Network traffic graph
        fig, self.ax_net = plt.subplots(figsize=(7, 3), dpi=100)
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
                proto = 'TCP' if conn.type == socket.SOCK_STREAM else 'UDP'
                self.connection_tree.insert('', 'end', values=(proto, laddr, raddr, conn.status, conn.pid or "N/A"))
        except (psutil.AccessDenied, PermissionError):
            self.connection_tree.insert('', 'end', values=("Access", "denied", "", "", ""))

    def update_network_traffic_graph(self):
        current_net_io = psutil.net_io_counters()
        elapsed = 1  # seconds

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

        step = max(1, len(self.timestamps)//10)
        self.ax_net.set_xticks(range(0, len(self.timestamps), step))
        self.ax_net.set_xticklabels(self.timestamps[::step], rotation=30, ha='right')

        self.canvas_net.draw()
        self.last_net_io = current_net_io


if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkMonitorApp(root)
    root.mainloop()
