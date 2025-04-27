# Imports
import customtkinter
import mysql.connector
import tkinter.messagebox
from mysql.connector import Error
from PIL import Image

# -------- Functions --------

def login():
    username = username_entry.get()
    password = password_entry.get()

    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="password",  # Your MySQL password 
            database="database_name",          # Your database name
            port=3306
        )
        cursor = mydb.cursor()

        cursor.execute(
            "SELECT role FROM users WHERE username=%s AND password=%s", 
            (username, password)
        )
        result = cursor.fetchone()

        if result:
            role = result[0]

            # Clear the current window
            for widget in root.winfo_children():
                widget.destroy()

            if role == "admin":
                open_admin_dashboard()
            else:
                open_user_dashboard()
        else:
            tkinter.messagebox.showerror('Error', 
                                         'Wrong credentials')

    except Error as e:
        print("Error while connecting to MySQL:", e)
        tkinter.messagebox.showerror('Error', 
                                     'Database connection error')

    finally:
        if 'mydb' in locals() and mydb.is_connected():
            cursor.close()
            mydb.close()

def open_admin_dashboard():
    for widget in root.winfo_children():
        widget.destroy()

    customtkinter.CTkLabel(root, 
                           text="Welcome Admin", 
                           font=("Helvetica", 24)).pack(pady=20)

    # Load the icon
    try:
        # Add full path to the icon if needed
        image = customtkinter.CTkImage(light_image=Image.open("icon.png"), size=(150, 150))
        
        # Check if the image is successfully loaded
        print("Image loaded successfully")
        
        icon_button = customtkinter.CTkButton(
            root,
            image=image,
            text="",  # No text
            command=open_user_management,
            width=160,
            height=160
        )
        icon_button.pack(pady=20)
        
    except Exception as e:
        print(f"Error loading icon: {e}")
        tkinter.messagebox.showerror("Error", 
                                     "Icon not found or failed to load.")

def open_user_management():
    user_window = customtkinter.CTkToplevel()
    user_window.title("User Management")
    user_window.geometry("600x600")

    customtkinter.CTkLabel(user_window, 
                           text="Manage Users", 
                           font=("Helvetica", 24)).pack(pady=20)

    customtkinter.CTkButton(user_window, 
                            text="View Users", 
                            command=view_users).pack(pady=10)
    customtkinter.CTkButton(user_window, 
                            text="Add User", 
                            command=lambda: user_form("add")).pack(pady=10)
    customtkinter.CTkButton(user_window, 
                            text="Edit User", 
                            command=lambda: user_form("edit")).pack(pady=10)
    customtkinter.CTkButton(user_window, 
                            text="Delete User", 
                            command=lambda: user_form("delete")).pack(pady=10)

def view_users():
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="password",  # Your MySQL password 
            database="database_name",          # Your database name
            port=3306
        )
        cursor = mydb.cursor()
        cursor.execute("SELECT id, username, password, role FROM users")
        users = cursor.fetchall()

        users_text = ""
        for user in users:
            users_text += f"ID: {user[0]}, Username: {user[1]}, Password: {user[2]}, Role: {user[3]}\n"

        tkinter.messagebox.showinfo("All Users", users_text)

    except Error as e:
        print("Error while fetching users:", e)
        tkinter.messagebox.showerror('Error', 
                                     'Database error')

    finally:
        if 'mydb' in locals() and mydb.is_connected():
            cursor.close()
            mydb.close()

def user_form(action):
    window = customtkinter.CTkToplevel()
    window.title(f"{action.capitalize()} User")
    window.geometry("400x500")

    if action in ["edit", "delete"]:
        customtkinter.CTkLabel(window, 
                               text="User ID (for edit/delete):").pack(pady=(10, 0))
        id_entry = customtkinter.CTkEntry(window)
        id_entry.pack(pady=(0, 10))

    if action in ["add", "edit"]:
        customtkinter.CTkLabel(window, 
                               text="Username:").pack(pady=(10, 0))
        username_entry = customtkinter.CTkEntry(window)
        username_entry.pack(pady=(0, 10))

        customtkinter.CTkLabel(window, 
                               text="Password:").pack(pady=(10, 0))
        password_entry = customtkinter.CTkEntry(window, 
                                                show="*")
        password_entry.pack(pady=(0, 10))

        customtkinter.CTkLabel(window, 
                               text="Role (admin/user):").pack(pady=(10, 0))
        role_entry = customtkinter.CTkEntry(window)
        role_entry.pack(pady=(0, 10))

    def perform_action():
        try:
            mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="password",  # Your MySQL password 
            database="database_name",          # Your database name
            port=3306
            )
            cursor = mydb.cursor()

            if action == "add":
                new_username = username_entry.get()
                new_password = password_entry.get()
                new_role = role_entry.get()

                if new_username and new_password and new_role:
                    cursor.execute(
                        "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", 
                        (new_username, 
                         new_password, 
                         new_role)
                    )
                    mydb.commit()
                    tkinter.messagebox.showinfo('Success', 
                                                'User added successfully')
                else:
                    tkinter.messagebox.showerror('Error', 
                                                 'All fields are required')

            elif action == "edit":
                user_id = id_entry.get()
                new_username = username_entry.get()
                new_password = password_entry.get()
                new_role = role_entry.get()

                fields = []
                values = []

                if new_username:
                    fields.append("username=%s")
                    values.append(new_username)
                if new_password:
                    fields.append("password=%s")
                    values.append(new_password)
                if new_role:
                    fields.append("role=%s")
                    values.append(new_role)

                if fields and user_id:
                    values.append(user_id)
                    sql = f"UPDATE users SET {', '.join(fields)} WHERE id=%s"
                    cursor.execute(sql, tuple(values))
                    mydb.commit()
                    tkinter.messagebox.showinfo('Success', 
                                                'User updated successfully')
                else:
                    tkinter.messagebox.showerror('Error', 
                                                 'Fill fields and provide User ID')

            elif action == "delete":
                user_id = id_entry.get()

                if user_id:
                    cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
                    mydb.commit()
                    tkinter.messagebox.showinfo('Success', 
                                                'User deleted successfully')
                else:
                    tkinter.messagebox.showerror('Error', 
                                                 'User ID required')

        except Error as e:
            print(f"Error during {action}:", e)
            tkinter.messagebox.showerror('Error', 
                                         'Database error')

        finally:
            if 'mydb' in locals() and mydb.is_connected():
                cursor.close()
                mydb.close()
                window.destroy()

    customtkinter.CTkButton(window, 
                            text=f"{action.capitalize()} User", 
                            command=perform_action).pack(pady=20)
    
def open_user_dashboard():
        customtkinter.CTkLabel(root, 
                                       text="Hello", 
                                       font=("Helvetica", 24)).pack(pady=20)

# -------- Main App Window --------

# Setting appearance mode
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

root = customtkinter.CTk()
root.geometry("1200x800")
root.title("Test")

customtkinter.CTkLabel(root, 
                       text="", 
                       font=("Helvetica", 24)).pack(pady=(40, 10))
customtkinter.CTkLabel(root, 
                       text="", 
                       font=("Helvetica", 24)).pack(pady=(40, 10))

customtkinter.CTkLabel(root, 
                       text="Username:", 
                       font=("Helvetica", 16)).pack(pady=(10, 0))
username_entry = customtkinter.CTkEntry(root, 
                                        placeholder_text="Enter your username...")
username_entry.pack(pady=(0, 10))

customtkinter.CTkLabel(root, 
                       text="Password:", 
                       font=("Helvetica", 16)).pack(pady=(10, 0))
password_entry = customtkinter.CTkEntry(root, 
                                        placeholder_text="Enter your password...", 
                                        show="*")
password_entry.pack(pady=(0, 20))

customtkinter.CTkButton(root, 
                        text="Login", 
                        command=login).pack(pady=10)

root.mainloop()