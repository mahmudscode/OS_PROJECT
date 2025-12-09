import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import pyudev

class USBMonitorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("USB Device Monitor ⚡")
        self.master.geometry("800x600")
        self.master.resizable(True, True)

        self.create_ui()
        self.monitor_usb_devices()
        self.start_usb_event_listener()
    
    def create_ui(self):
        self.usb_frame = ttk.LabelFrame(self.master, text="🔌 Connected USB Devices")
        self.usb_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.usb_tree = ttk.Treeview(self.usb_frame, columns=("Bus", "Device", "ID", "Details"), show="headings", height=15)
        for col in ("Bus", "Device", "ID", "Details"):
            self.usb_tree.heading(col, text=col)
            self.usb_tree.column(col, width=150 if col != "Details" else 400)
        self.usb_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        # Add vertical scrollbar
        scrollbar = ttk.Scrollbar(self.usb_frame, orient=tk.VERTICAL, command=self.usb_tree.yview)
        self.usb_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        button_frame = ttk.Frame(self.master)
        button_frame.pack(pady=5)
        
        self.refresh_button = ttk.Button(button_frame, text="🔄 Refresh USB Devices", command=self.monitor_usb_devices)
        self.refresh_button.grid(row=0, column=0, padx=5)
        
        self.details_button = ttk.Button(button_frame, text="🔍 Show Device Details", command=self.show_device_details)
        self.details_button.grid(row=0, column=1, padx=5)
        
        self.details_label = ttk.Label(self.master, text="Device details will appear here...", wraplength=750, justify="left")
        self.details_label.pack(pady=10)

    def monitor_usb_devices(self):
        """Retrieve and display currently connected USB devices using lsusb."""
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

    def show_device_details(self):
        """Show detailed information about the selected device using udevadm info."""
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
            self.details_label.config(text=(output[:1000] + "...") if len(output) > 1000 else output)
        except subprocess.CalledProcessError as e:
            self.details_label.config(text=f"❌ Error fetching details:\n{e}")

    def start_usb_event_listener(self):
        """Start a thread to monitor USB events."""
        threading.Thread(target=self.usb_event_listener, daemon=True).start()

    def usb_event_listener(self):
        """Real-time USB event monitoring using pyudev."""
        context = pyudev.Context()
        monitor = pyudev.Monitor.from_netlink(context)
        monitor.filter_by(subsystem='usb')
        for device in iter(monitor.poll, None):
            # Update UI in main thread
            self.master.after(100, self.monitor_usb_devices)


if __name__ == "__main__":
    root = tk.Tk()
    app = USBMonitorApp(root)
    root.mainloop()
