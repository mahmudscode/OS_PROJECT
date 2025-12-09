import tkinter as tk
from tkinter import ttk, messagebox
from cryptography.fernet import Fernet
import pyperclip

class SimpleEncryptionDecryptionTool:
    def __init__(self, master):
        self.master = master
        self.master.title("Simple Encryption/Decryption Tool 🔐")
        self.master.geometry("650x450")
        self.master.resizable(False, False)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=('Segoe UI', 10), padding=6)
        style.configure("TLabel", font=('Segoe UI', 11))

        # Encryption Frame
        self.encryption_frame = ttk.LabelFrame(master, text="🔐 Encryption", padding=15)
        self.encryption_frame.pack(padx=10, pady=10, fill='x')

        ttk.Label(self.encryption_frame, text="Encryption Key:").grid(row=0, column=0, sticky='w')
        self.key_entry = ttk.Entry(self.encryption_frame, width=50)
        self.key_entry.grid(row=0, column=1, pady=5)

        ttk.Button(self.encryption_frame, text="Generate Key", command=self.generate_key).grid(row=1, column=0, sticky='w')
        ttk.Button(self.encryption_frame, text="Copy Key", command=self.copy_key_to_clipboard).grid(row=1, column=1, sticky='e')

        ttk.Label(self.encryption_frame, text="Enter Message:").grid(row=2, column=0, sticky='w')
        self.message_entry = ttk.Entry(self.encryption_frame, width=50)
        self.message_entry.grid(row=2, column=1, pady=5)

        ttk.Button(self.encryption_frame, text="Encrypt", command=self.encrypt_message).grid(row=3, column=0, sticky='w', pady=5)

        self.encrypted_message_display = ttk.Label(self.encryption_frame, text="", foreground="green", wraplength=500)
        self.encrypted_message_display.grid(row=4, column=0, columnspan=2, pady=5)

        ttk.Button(self.encryption_frame, text="Copy Encrypted", command=self.copy_encrypted_message).grid(row=5, column=1, sticky='e')

        # Decryption Frame
        self.decryption_frame = ttk.LabelFrame(master, text="🔓 Decryption", padding=15)
        self.decryption_frame.pack(padx=10, pady=10, fill='x')

        ttk.Label(self.decryption_frame, text="Encryption Key:").grid(row=0, column=0, sticky='w')
        self.decrypted_key_entry = ttk.Entry(self.decryption_frame, width=50)
        self.decrypted_key_entry.grid(row=0, column=1, pady=5)

        ttk.Label(self.decryption_frame, text="Encrypted Message:").grid(row=1, column=0, sticky='w')
        self.decrypted_message_entry = ttk.Entry(self.decryption_frame, width=50)
        self.decrypted_message_entry.grid(row=1, column=1, pady=5)

        ttk.Button(self.decryption_frame, text="Decrypt", command=self.decrypt_message).grid(row=2, column=0, sticky='w', pady=5)

        self.decrypted_message_result = ttk.Label(self.decryption_frame, text="", foreground="blue", wraplength=500)
        self.decrypted_message_result.grid(row=3, column=0, columnspan=2, pady=5)

    # --- Functions ---
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
        except Exception:
            self.encrypted_message_display.config(text="❌ Invalid Key!")

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
            self.decrypted_message_result.config(text="❌ Invalid key or message!")

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


if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleEncryptionDecryptionTool(root)
    root.mainloop()
