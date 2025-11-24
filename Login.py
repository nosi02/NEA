import customtkinter as ctk
from tkinter import messagebox
class LoginScreen(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Login")
        self.geometry("300x200")
        self.grid_columnconfigure(0, weight=1)
        self.label = ctk.CTkLabel(self,text="Please Enter Password", font=ctk.CTkFont(size=16, weight="bold"))
        self.label.grid(row=0, column=0, padx=10, pady=(30, 10), sticky="ew")


        self.password_entry= ctk.CTkEntry(self, placeholder_text="Password",show = "*")
        self.password_entry.grid(row=1, column=0, pady=(0, 20), padx=20, sticky="ew")

        self.login_button = ctk.CTkButton(self,text="Login", command=self.check_login)
        self.login_button.grid(row=2, column=0, pady=10, padx=20, sticky="ew")

        self.error_label = ctk.CTkLabel(self, text="", text_color="red")
        self.error_label.grid(row=3, column=0, pady=5)
        #trigger login
        self.bind('<Return>', lambda event: self.check_login())

    def check_login(self):
        from GUI import App
        entered_password = self.password_entry.get()
        if entered_password == "admin123":
            self.destroy()
            app = App()
            app.mainloop()
        else:
            self.error_label.configure(text="Incorrect Password")
            self.password_entry.delete(0, "end")  # Clear the box

if __name__ == "__main__":
    login = LoginScreen()
    login.mainloop()
