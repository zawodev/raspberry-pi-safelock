import customtkinter as ctk
from tkinter import ttk, messagebox, colorchooser  # still need these from tkinter
from database import (
    create_connection,
    create_tables,
    add_user,
    add_login_record,
    get_all_login_records,
    get_all_requests,
    add_request,
    delete_request,
    get_all_users,
    delete_user
)
from utils import pick_color_factory, compare

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self, db_path="mini-project/server/database.db"):
        super().__init__()
        self.title("GUI Admin App")


        self.geometry("600x400")
        self.resizable(False, False)


        self.conn = create_connection(db_path)
        if self.conn:
            create_tables(self.conn)


        label = ctk.CTkLabel(self, text="Menu główne", 
                             font=ctk.CTkFont(size=16, weight="bold"))
        label.pack(pady=20)

        btn_show_users = ctk.CTkButton(self, text="Pokaż użytkowników",
                                       width=200,
                                       command=self.show_users_window)
        btn_show_users.pack(pady=5)

        btn_new_user = ctk.CTkButton(self, text="Dodaj nowego użytkownika",
                                     width=200,
                                     command=self.show_add_user_window)
        btn_new_user.pack(pady=5)

        btn_login_record = ctk.CTkButton(self, text="Pokaż ewidencję logowań",
                                         width=200,
                                         command=self.show_login_record_window)
        btn_login_record.pack(pady=5)

        btn_requests = ctk.CTkButton(self, text="Pokaż prośby o rejestrację",
                                     width=200,
                                     command=self.show_requests_window)
        btn_requests.pack(pady=5)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#2b2b2b",
                        foreground="white",
                        rowheight=25,
                        fieldbackground="#2b2b2b")
        style.map("Treeview", background=[("selected", "#1f538d")])


    def add_request_mqtt(self, type, msg_str):
        if type == "RFID":
            print(msg_str)
            uid_num, now_str = msg_str.split(",")

            users = get_all_users(self.conn)
            
            print(users)
            user_ids = [user[0] for user in users]

            if uid_num in user_ids:
                return "VALID"
            else:
                add_request(self.conn, uid_num)
                return "INVALID"

        elif type == "ENCODER":
            rfid, code = msg_str.split(":")
            code = [int(x) for x in code.split(",")]
            users = get_all_users(self.conn)
            user_ids = [user[0] for user in users]
            safe_codes = [user[3] for user in users]

            for user_id in user_ids:
                if user_id == rfid:
                    safe_code = safe_codes[user_ids.index(user_id)][1:len(safe_codes[user_ids.index(user_id)])-1].split(", ")
                    safe_code = [int(x) for x in safe_code]
                    if compare(safe_code, code):
                        add_login_record(self.conn, rfid, "ACCEPTED")
                        return "VALID"

                    else:
                        add_login_record(self.conn, rfid, "DENIED")
                        return "INVALID"
        else:
            return "INVALID"
                    

    # -------------------------------------------------------
    # 1) Window: Add New User
    # -------------------------------------------------------
    def show_add_user_window(self):
        win = ctk.CTkToplevel(self)
        win.title("Dodaj nowego użytkownika")
        win.geometry("450x500")
        win.resizable(False, False)

        ctk.CTkLabel(win, text="ID Użytkownika (ID karty):").grid(row=0, column=0, 
                                                                 sticky="w", padx=5, pady=5)
        ctk.CTkLabel(win, text="Login:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ctk.CTkLabel(win, text="Hasło:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ctk.CTkLabel(win, text="Kombinacja sejfu (8 liczb 0..359):").grid(row=3, column=0, 
                                                                         sticky="w", padx=5, pady=5)

        entry_user_id = ctk.CTkEntry(win, width=200)
        entry_login = ctk.CTkEntry(win, width=200)
        entry_password = ctk.CTkEntry(win, show="*", width=200)

        entry_user_id.grid(row=0, column=1, padx=5, pady=5)
        entry_login.grid(row=1, column=1, padx=5, pady=5)
        entry_password.grid(row=2, column=1, padx=5, pady=5)

        frame_safe = ctk.CTkFrame(win)
        frame_safe.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        entry_safe_list = []
        for i in range(8):
            sub_frame = ctk.CTkFrame(frame_safe)
            sub_frame.pack(side="top", anchor="w", pady=2)

            lbl_i = ctk.CTkLabel(sub_frame, text=f"{i+1}.")
            lbl_i.pack(side="left")

            e = ctk.CTkEntry(sub_frame, width=50)
            e.pack(side="left", padx=3)
            entry_safe_list.append(e)

            btn_color = ctk.CTkButton(sub_frame, text="Kolor", width=50,
                                      command=pick_color_factory(e))
            btn_color.pack(side="left", padx=2)

        def on_add():
            user_id = entry_user_id.get().strip()
            login = entry_login.get().strip()
            password = entry_password.get().strip()

            if not user_id or not login or not password:
                messagebox.showerror("Error", "Uzupełnij wszystkie pola: ID, Login, Hasło.")
                return

            safe_comb_values = []
            for i, e in enumerate(entry_safe_list):
                val_str = e.get().strip()
                if not val_str:
                    messagebox.showerror("Error", f"Brak wartości dla pola nr {i+1}.")
                    return
                try:
                    val_int = int(val_str)
                except ValueError:
                    messagebox.showerror("Error", f"Niepoprawna liczba w polu nr {i+1}: '{val_str}'")
                    return
                if not (0 <= val_int <= 359):
                    messagebox.showerror("Error", f"Wartość w polu nr {i+1} musi być w zakresie 0..359.")
                    return
                safe_comb_values.append(val_int)

            if len(safe_comb_values) != 8:
                messagebox.showerror("Error", "Musisz podać dokładnie 8 liczb (0..359).")
                return

            # Add to database
            add_user(self.conn, user_id, login, password, safe_comb_values)
            messagebox.showinfo("OK", f"Dodano nowego użytkownika: {user_id}")
            win.destroy()

        btn_save = ctk.CTkButton(win, text="Dodaj", command=on_add)
        btn_save.grid(row=4, column=1, pady=10, sticky="e")

    # -------------------------------------------------------
    # 2) Window: Show Ewidencja Logowań
    # -------------------------------------------------------
    def show_login_record_window(self):
        win = ctk.CTkToplevel(self)
        win.title("Ewidencja logowań")
        win.geometry("900x400")
        win.resizable(False, False)

        records = get_all_login_records(self.conn)

        tree = ttk.Treeview(win, columns=("login_record_id", "user_id", "date_time", "status"), 
                            show="headings")
        tree.heading("login_record_id", text="Login Record ID")
        tree.heading("user_id", text="User ID")
        tree.heading("date_time", text="Date/Time")
        tree.heading("status", text="Status")
        tree.pack(fill="both", expand=True)

        for row in records:
            tree.insert("", ctk.END, values=row)

    # -------------------------------------------------------
    # 3) Window: Process Requests
    # -------------------------------------------------------
    def show_requests_window(self):
        win = ctk.CTkToplevel(self)
        win.title("Prośby o rejestrację")
        win.geometry("1100x500")
        win.resizable(False, False)

        # Left frame: request list
        frame_left = ctk.CTkFrame(win)
        frame_left.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(frame_left, text="Lista próśb:").pack(anchor="w")

        tree_req = ttk.Treeview(frame_left, columns=("request_id", "user_id", "date_time"), 
                                show="headings", height=10)
        tree_req.heading("request_id", text="Req ID")
        tree_req.heading("user_id", text="Requested user_id")
        tree_req.heading("date_time", text="Date/Time")
        tree_req.pack(fill="both", expand=True)

        requests = get_all_requests(self.conn)
        for row in requests:
            tree_req.insert("", ctk.END, values=row)


        # Right frame: form to add user from request
        frame_right = ctk.CTkFrame(win)
        frame_right.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(frame_right, text="Wybrane ID (Request ID):").grid(row=0, column=0, 
                                                                       sticky="w", padx=5, pady=5)
        ctk.CTkLabel(frame_right, text="Login:").grid(row=1, column=0, 
                                                      sticky="w", padx=5, pady=5)
        ctk.CTkLabel(frame_right, text="Hasło:").grid(row=2, column=0, 
                                                      sticky="w", padx=5, pady=5)
        ctk.CTkLabel(frame_right, text="Kombinacja (8 liczb 0..359):").grid(row=3, column=0, 
                                                                           sticky="w", padx=5, pady=5)

        entry_req_id = ctk.CTkEntry(frame_right, width=150)
        entry_login = ctk.CTkEntry(frame_right, width=200)
        entry_password = ctk.CTkEntry(frame_right, width=200, show="*")

        entry_req_id.grid(row=0, column=1, padx=5, pady=5)
        entry_login.grid(row=1, column=1, padx=5, pady=5)
        entry_password.grid(row=2, column=1, padx=5, pady=5)

        frame_right_safe = ctk.CTkFrame(frame_right)
        frame_right_safe.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        entry_req_safe_list = []
        for i in range(8):
            sub_frame = ctk.CTkFrame(frame_right_safe)
            sub_frame.pack(side="top", anchor="w", pady=2)

            lbl_i = ctk.CTkLabel(sub_frame, text=f"{i+1}.")
            lbl_i.pack(side="left")

            e = ctk.CTkEntry(sub_frame, width=50)
            e.pack(side="left", padx=3)
            entry_req_safe_list.append(e)

            btn_color = ctk.CTkButton(sub_frame, text="Kolor", width=50,
                                      command=pick_color_factory(e))
            btn_color.pack(side="left", padx=2)

        def on_request_select(event):
            selected = tree_req.focus()
            if not selected:
                return
            values = tree_req.item(selected, "values")  # (request_id, user_id, date_time)
            req_id = values[0]
            entry_req_id.delete(0, ctk.END)
            entry_req_id.insert(0, str(req_id))

        tree_req.bind("<<TreeviewSelect>>", on_request_select)

        def on_add_user_from_request():
            req_id_str = entry_req_id.get().strip()
            new_login = entry_login.get().strip()
            new_pass = entry_password.get().strip()

            if not req_id_str or not new_login or not new_pass:
                messagebox.showerror("Error", "Wypełnij pola Request ID, Login, Hasło.")
                return

            try:
                req_id = int(req_id_str)
            except ValueError:
                messagebox.showerror("Error", "Niepoprawny Request ID.")
                return

            # Get request from DB
            all_req = get_all_requests(self.conn)
            selected_req = None
            for r in all_req:
                # r = (request_id, user_id, date_time)
                if r[0] == req_id:
                    selected_req = r
                    break

            if not selected_req:
                messagebox.showerror("Error", "Brak takiego requestu w bazie.")
                return

            requested_user_id = selected_req[1]  # user_id from that row

            # Gather 8 numbers
            safe_comb_values = []
            for i, e in enumerate(entry_req_safe_list):
                val_str = e.get().strip()
                if not val_str:
                    messagebox.showerror("Error", f"Brak wartości w polu nr {i+1}.")
                    return
                try:
                    val_int = int(val_str)
                except ValueError:
                    messagebox.showerror("Error", f"Niepoprawna liczba w polu nr {i+1}: '{val_str}'")
                    return
                if not (0 <= val_int <= 359):
                    messagebox.showerror("Error", f"Wartość w polu nr {i+1} musi być w zakresie 0..359.")
                    return
                safe_comb_values.append(val_int)

            if len(safe_comb_values) != 8:
                messagebox.showerror("Error", "Musisz podać dokładnie 8 liczb (0..359).")
                return

            add_user(self.conn, requested_user_id, new_login, new_pass, safe_comb_values)
            messagebox.showinfo("OK", f"Dodano użytkownika o ID: {requested_user_id}")

            delete_request(self.conn, req_id)
            messagebox.showinfo("OK", "Rekord request został usunięty.")

            # Refresh the request list
            for item in tree_req.get_children():
                tree_req.delete(item)
            updated_requests = get_all_requests(self.conn)
            for row in updated_requests:
                tree_req.insert("", ctk.END, values=row)

            # Clear form
            entry_req_id.delete(0, ctk.END)
            entry_login.delete(0, ctk.END)
            entry_password.delete(0, ctk.END)
            for e in entry_req_safe_list:
                e.delete(0, ctk.END)

        btn_add_user = ctk.CTkButton(frame_right, text="Dodaj", command=on_add_user_from_request)
        btn_add_user.grid(row=4, column=1, padx=5, pady=10, sticky="e")

    # -------------------------------------------------------
    # 4) Window: Show and Delete Users
    # -------------------------------------------------------
    def show_users_window(self):
        win = ctk.CTkToplevel(self)
        win.title("Lista Użytkowników")
        win.geometry("1000x400")
        win.resizable(False, False)

        users = get_all_users(self.conn)

        frame_top = ctk.CTkFrame(win)
        frame_top.pack(fill="both", expand=True, padx=10, pady=10)

        tree_users = ttk.Treeview(frame_top, columns=("id", "login", "password", "safe_combination"), 
                                  show="headings", height=10)
        tree_users.heading("id", text="ID")
        tree_users.heading("login", text="Login")
        tree_users.heading("password", text="Hasło")
        tree_users.heading("safe_combination", text="Kombinacja do sejfu")

        tree_users.pack(side="left", fill="both", expand=True)

        # Vertical scrollbar
        vsb = ttk.Scrollbar(frame_top, orient="vertical", command=tree_users.yview)
        tree_users.configure(yscroll=vsb.set)
        vsb.pack(side="right", fill="y")

        # Insert data
        for u in users:
            tree_users.insert("", ctk.END, values=u)

        frame_bottom = ctk.CTkFrame(win)
        frame_bottom.pack(fill="x", padx=10, pady=10)

        def on_delete_user():
            selected = tree_users.focus()
            if not selected:
                messagebox.showwarning("Warning", "Nie wybrano żadnego użytkownika.")
                return
            values = tree_users.item(selected, "values")  # (id, login, password, safe_combination)
            user_id = values[0]

            if messagebox.askyesno("Potwierdzenie", f"Czy na pewno usunąć użytkownika o ID '{user_id}'?"):
                delete_user(self.conn, user_id)
                # Refresh
                tree_users.delete(*tree_users.get_children())
                new_users = get_all_users(self.conn)
                for u2 in new_users:
                    tree_users.insert("", ctk.END, values=u2)

        btn_delete = ctk.CTkButton(frame_bottom, text="Usuń", command=on_delete_user)
        btn_delete.pack(side="right")


if __name__ == "__main__":
    app = App("mini-project/server/database.db")
    app.mainloop()
