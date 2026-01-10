import customtkinter as ctk
import Database as db
from tkinter import messagebox

# Attempt to import the main GUI
try:
    from GUI import App
except ImportError:
    print("Warning: Could not import 'App' from 'GUI.py'. Check filename.")
    App = None


class LoginScreen(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Pharmacy System Login")
        self.geometry("350x380")
        self.grid_columnconfigure(0, weight=1)
        self.master_recovery_key = "pharmacy_recovery_2024"
        self.label = ctk.CTkLabel(self, text="Pharmacy Inventory Manager", font=ctk.CTkFont(size=18, weight="bold"))
        self.label.grid(row=0, column=0, padx=10, pady=(40, 10), sticky="ew")
        self.subtitle = ctk.CTkLabel(self, text="Secure Login", text_color="gray")
        self.subtitle.grid(row=1, column=0, pady=(0, 20))

        # Password Entry
        self.password_entry = ctk.CTkEntry(self, placeholder_text="Enter Admin Password", show="*", width=220,height=35)
        self.password_entry.grid(row=2, column=0, pady=10, padx=20)

        # Login Button
        self.login_button = ctk.CTkButton(self, text="Login", command=self.check_login, corner_radius=8, width=220, height=35)
        self.login_button.grid(row=3, column=0, pady=10, padx=20)

        # Forgot Password Button
        self.forgot_btn = ctk.CTkButton(self, text="Forgot Password?",
                                        fg_color="transparent",
                                        text_color=("gray20", "gray80"),
                                        hover=False,
                                        font=("Arial", 11, "underline"),
                                        command=self.open_reset_window)
        self.forgot_btn.grid(row=4, column=0, pady=10)

        # Bind the Enter key to the login function
        self.bind('<Return>', lambda event: self.check_login())

    def check_login(self):
        entered_text = self.password_entry.get()
        # Hash input
        input_hash = db.hash_password(entered_text)
        # Get hash from the DB
        stored_hash = db.get_stored_hash()
        if input_hash == stored_hash:
            if App:
                self.destroy()
                main_window = App()
                main_window.mainloop()
            else:
                messagebox.showerror("Error", "Main Application (App class) not found in GUI.py")
        else:
            messagebox.showerror("Access Denied", "Incorrect Password.")
            self.password_entry.delete(0, "end")

    def open_reset_window(self):
        reset_win = ctk.CTkToplevel(self)
        reset_win.title("Reset Password")
        reset_win.geometry("300x350")
        reset_win.attributes('-topmost', True)
        reset_win.grab_set()  # Forces user to interact with this window only
        ctk.CTkLabel(reset_win, text="Security Recovery", font=("Arial", 14, "bold")).pack(pady=20)

        key_entry = ctk.CTkEntry(reset_win, placeholder_text="Master Recovery Key", width=200)
        key_entry.pack(pady=10)

        new_pw_entry = ctk.CTkEntry(reset_win, placeholder_text="New Password", show="*", width=200)
        new_pw_entry.pack(pady=10)

        def perform_reset():
            if key_entry.get() == self.master_recovery_key:
                new_pw = new_pw_entry.get()
                if new_pw:
                    # CRITICAL FIX: Update the database hash permanently
                    db.update_stored_password(new_pw)
                    messagebox.showinfo("Success", "Password updated successfully in database!")
                    reset_win.destroy()
                else:
                    messagebox.showerror("Error", "New password cannot be empty.")
            else:
                messagebox.showerror("Error", "Invalid Master Recovery Key.")

        ctk.CTkButton(reset_win, text="Apply New Password", command=perform_reset).pack(pady=30)


if __name__ == "__main__":
    login = LoginScreen()
    login.mainloop()