import subprocess
import sys
from datetime import date, datetime, timedelta
from tkinter import *
from tkinter import ttk, messagebox
import mysql.connector
import os
import random
import re
from tkcalendar import DateEntry


# ================= DATABASE CONNECTION =================
def connect_db():
    """Centralized database connection"""
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="grocery"
    )


# ================= LOGIN CLASS =================
class LoginClass:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        self.root.geometry("450x350+550+100")
        self.root.resizable(0, 0)
        self.root.config(bg="#f3f1e8")

        # Variables
        self.emailEntry = None
        self.PassEntry = None

        self.create_login_ui()

    def create_login_ui(self):
        """Create login interface"""
        loginLabel = Label(self.root, text="Welcome back", font=('Garamond', 20, 'bold'),
                           fg="#0a3e34", bg="#f3f1e8")
        loginLabel.place(x=140, y=40)

        Emaillabel = Label(self.root, text="Email:", font=('Garamond', 13, 'bold'),
                           bg="#f3f1e8", fg="#0a3e34")
        Emaillabel.place(x=72, y=115)

        self.emailEntry = Entry(self.root, width=40)
        self.emailEntry.place(x=128, y=118)

        Passlabel = Label(self.root, text="Password:", font=('Garamond', 13, 'bold'),
                          bg="#f3f1e8", fg="#0a3e34")
        Passlabel.place(x=72, y=185)

        self.PassEntry = Entry(self.root, show='*', width=36)
        self.PassEntry.place(x=155, y=188)

        loginBTN = Button(
            self.root,
            text="Login",
            font=('Garamond', 10, 'bold'),
            fg='#0a3e34',
            bg='#e9e6d5',
            width=10,
            height=1,
            command=self.login_user)
        loginBTN.place(x=190, y=260)

    def login_user(self):
        """Handle user login"""
        email = self.emailEntry.get()
        password = self.PassEntry.get()

        if not email or not password:
            messagebox.showerror("Error", "All fields are required")
            return

        try:
            db = connect_db()
            cursor = db.cursor()

            query = """
                SELECT EmpID, Role
                FROM Employees
                WHERE Email=%s AND Password=%s
            """
            cursor.execute(query, (email, password))
            result = cursor.fetchone()

            if result:
                emp_id = result[0]
                role = result[1].lower()
                messagebox.showinfo("Success", f"Login Successful as {role.capitalize()}")

                self.root.destroy()

                # Open appropriate interface based on role
                if role == "admin":
                    self.open_dashboard(emp_id)
                elif role == "cashier":
                    self.open_cashier(emp_id)
                else:
                    messagebox.showerror("Error", "User role not recognized")

            else:
                messagebox.showerror("Error", "Invalid email or password")

            cursor.close()
            db.close()

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))

    def open_dashboard(self, emp_id):
        """Open dashboard for admin users"""
        dashboard_root = Tk()
        dashboard_app = DashboardClass(dashboard_root, emp_id)
        dashboard_root.mainloop()

    def open_cashier(self, emp_id):
        """Open cashier interface for cashier users"""
        cashier_root = Tk()
        cashier_app = CashierClass(cashier_root, emp_id)
        cashier_root.mainloop()


# ================= DASHBOARD CLASS =================
class DashboardClass:
    def __init__(self, root, emp_id):
        self.root = root
        self.emp_id = emp_id
        self.admin_name = self.get_admin_name(self.emp_id)

        # Create dashboard UI
        self.create_dashboard_ui()

        # Update dashboard
        self.update_time()
        self.update_dashboard_stats()
        self.refresh_graph()

    def get_admin_name(self, emp_id):
        """Get admin name from database"""
        if not emp_id:
            return "Unknown Admin"
        conn = None
        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("SELECT FirstName, LastName FROM Employees WHERE EmpID=%s AND Role='Admin'", (emp_id,))
            res = cur.fetchone()
            if res:
                return f"{res[0]} {res[1]}"
            return "Unknown Admin"
        except mysql.connector.Error:
            return "Error"
        finally:
            if conn:
                conn.close()

    def create_dashboard_ui(self):
        """Create dashboard interface"""
        self.root.title("Dashboard")
        self.root.geometry("1500x768+10+5")
        self.root.resizable(0, 0)
        self.root.config(bg='#e9e6d5')

        # Title
        titleLabel = Label(self.root,
                           compound="left",
                           text="Grocery Sales & Inventory Management System",
                           font=('Garamond', 25, 'bold'),
                           fg="white",
                           bg="#27693f",
                           anchor='center',
                           padx=10, pady=10)
        titleLabel.place(x=0, y=0, height=150, relwidth=1)

        # Logout button
        logout_btn = Button(
            self.root,
            text="Logout",
            font=('Garamond', 20, 'bold'),
            fg='#0a3e34',
            bg='#e9e6d5',
            command=self.logout
        )
        logout_btn.place(x=1230, y=40)

        # Date/Time label
        self.subLabel = Label(
            self.root,
            text="Loading...",
            font=('Garamond', 12, 'bold'),
            bg="#e9e6d5",
            fg="#0a3e34"
        )
        self.subLabel.place(x=0, y=125, relwidth=1)

        # Left menu frame
        leftFrame = Frame(self.root, background='#27693f')
        leftFrame.place(x=0, y=150, width=200, height=620)

        menuLabel = Label(leftFrame, text='Menu',
                          font=('Garamond', 20, 'bold'), bg='#27693f', fg='#e9e6d5')
        menuLabel.pack(fill=X, padx=0, pady=10)

        # Menu buttons
        self.create_menu_buttons(leftFrame)

        # Stats frames
        self.create_stats_frames()

        # Graph frame
        self.create_graph_frame()

    def create_menu_buttons(self, parent):
        """Create menu buttons"""
        # Employee button
        employee_btn = Button(parent, text='Employee',
                              font=('Garamond', 15, 'bold'),
                              fg='#0a3e34', bg='#e9e6d5',
                              width=15, height=1,
                              command=lambda: self.open_employee_form())
        employee_btn.pack(padx=0, pady=5)

        # Supplier button
        sup_btn = Button(parent, text='Supplier',
                         font=('Garamond', 15, 'bold'),
                         fg='#0a3e34', bg='#e9e6d5',
                         width=15, height=1,
                         command=lambda: self.open_supplier_form())
        sup_btn.pack(padx=0, pady=5)

        # Product button
        pr_btn = Button(parent, text='Product',
                        font=('Garamond', 15, 'bold'),
                        fg='#0a3e34', bg='#e9e6d5',
                        width=15, height=1,
                        command=lambda: self.open_product_form())
        pr_btn.pack(padx=0, pady=5)

        # Sales button
        sale_btn = Button(parent, text='Sales',
                          font=('Garamond', 15, 'bold'),
                          fg='#0a3e34', bg='#e9e6d5',
                          width=15, height=1,
                          command=lambda: self.open_sales_form())
        sale_btn.pack(padx=0, pady=5)

        # Cashier button
        cashier_btn = Button(parent, text='Cashier',
                             font=('Garamond', 15, 'bold'),
                             fg='#0a3e34', bg='#e9e6d5',
                             width=15, height=1,
                             command=self.open_cashier_window)
        cashier_btn.pack(padx=0, pady=5)

    def create_stats_frames(self):
        """Create statistics display frames"""
        # Employees frame
        emp_Frame = Frame(self.root, background='#27693f', bd=3, relief=RIDGE)
        emp_Frame.place(x=220, y=185, width=300, height=110)
        Label(emp_Frame, text="Total Employees", font=("Garamond", 18, "bold"),
              bg="#27693f", fg="#e9e6d5").place(x=30, y=15)
        self.emp_value = Label(emp_Frame, text="0", font=("Garamond", 30, "bold"),
                               bg="#27693f", fg="#e9e6d5")
        self.emp_value.place(x=120, y=55)

        # Suppliers frame
        sup_Frame = Frame(self.root, background='#27693f', bd=3, relief=RIDGE)
        sup_Frame.place(x=220, y=310, width=300, height=110)
        Label(sup_Frame, text="Total Suppliers", font=("Garamond", 18, "bold"),
              bg="#27693f", fg="#e9e6d5").place(x=30, y=15)
        self.sup_value = Label(sup_Frame, text="0", font=("Garamond", 30, "bold"),
                               bg="#27693f", fg="#e9e6d5")
        self.sup_value.place(x=120, y=55)

        # Products frame
        pr_Frame = Frame(self.root, background='#27693f', bd=3, relief=RIDGE)
        pr_Frame.place(x=220, y=435, width=300, height=110)
        Label(pr_Frame, text="Total Products", font=("Garamond", 18, "bold"),
              bg="#27693f", fg="#e9e6d5").place(x=30, y=15)
        self.pr_value = Label(pr_Frame, text="0", font=("Garamond", 30, "bold"),
                              bg="#27693f", fg="#e9e6d5")
        self.pr_value.place(x=120, y=55)

        # Sales frame
        sl_Frame = Frame(self.root, background='#27693f', bd=3, relief=RIDGE)
        sl_Frame.place(x=220, y=560, width=300, height=110)
        Label(sl_Frame, text="Total Sales", font=("Garamond", 18, "bold"),
              bg="#27693f", fg="#e9e6d5").place(x=30, y=15)
        self.sl_value = Label(sl_Frame, text="₱0", font=("Garamond", 30, "bold"),
                              bg="#27693f", fg="#e9e6d5")
        self.sl_value.place(x=80, y=55)

    def create_graph_frame(self):
        """Create graph display frame"""
        graph_Frame = Frame(self.root, background='white', bd=3, relief=RIDGE)
        graph_Frame.place(x=540, y=185, width=930, height=485)

        self.graph_title = Label(graph_Frame, text="Cashier Total Sales",
                                 font=("Garamond", 14, "bold"), bg="white", fg="#0a3e34")
        self.graph_title.place(x=10, y=10)

        self.graph_canvas = Canvas(graph_Frame, width=910, height=420, bg="white", highlightthickness=0)
        self.graph_canvas.place(x=10, y=40)

        # Graph controls
        self.create_graph_controls(graph_Frame)

    def create_graph_controls(self, parent):
        """Create graph control buttons"""
        self.graph_mode_var = StringVar(value="Cashiers")
        self.graph_period_var = StringVar(value="30 days")

        controls_frame = Frame(parent, bg="white")
        controls_frame.place(x=540, y=8, width=500, height=28)

        Label(controls_frame, text="Type:", font=("Garamond", 10, "bold"),
              bg="white", fg="#0a3e34").pack(side=LEFT, padx=(0, 4))

        mode_menu = OptionMenu(controls_frame, self.graph_mode_var, "Cashiers", "Daily")
        mode_menu.config(bg="#e9e6d5", fg="#0a3e34", activebackground="#dcd8c6")
        mode_menu.config(font=("Garamond", 10, "bold"))
        mode_menu["menu"].config(font=("Garamond", 10))
        mode_menu.pack(side=LEFT, padx=(0, 10))

        Label(controls_frame, text="Range:", font=("Garamond", 10, "bold"),
              bg="white", fg="#0a3e34").pack(side=LEFT, padx=(0, 4))

        period_menu = OptionMenu(controls_frame, self.graph_period_var, "7 days", "30 days", "90 days")
        period_menu.config(bg="#e9e6d5", fg="#0a3e34", activebackground="#dcd8c6")
        period_menu.config(font=("Garamond", 10, "bold"))
        period_menu["menu"].config(font=("Garamond", 10))
        period_menu.pack(side=LEFT, padx=(0, 10))

        refresh_btn = Button(controls_frame, text="Refresh", font=("Garamond", 10, "bold"),
                             fg="#0a3e34", bg="#e9e6d5", command=self.refresh_graph)
        refresh_btn.pack(side=LEFT, padx=(5, 0))

    def update_time(self):
        """Update time display"""
        current_date = date.today().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M:%S")
        self.subLabel.config(text=f"Welcome: {self.admin_name}      Date: {current_date}      Time: {current_time}")
        self.subLabel.after(1000, self.update_time)

    def update_dashboard_stats(self):
        """Update dashboard statistics"""
        emp_total = 0
        pr_total = 0
        sup_total = 0
        sales_total = 0.0

        conn = None
        try:
            conn = connect_db()
            cur = conn.cursor()

            cur.execute("SELECT COUNT(*) FROM employees WHERE Archived=0")
            emp_total = cur.fetchone()[0] or 0

            cur.execute("SELECT COUNT(*) FROM Product WHERE IsArchived=0")
            pr_total = cur.fetchone()[0] or 0

            cur.execute("SELECT COUNT(*) FROM Supplier WHERE IsArchived=0")
            sup_total = cur.fetchone()[0] or 0
        except mysql.connector.Error:
            pass
        finally:
            if conn:
                conn.close()

        # Calculate sales from bills
        try:
            if os.path.isdir("bills"):
                for fname in os.listdir("bills"):
                    if not fname.endswith(".txt"):
                        continue
                    try:
                        with open(os.path.join("bills", fname), "r") as f:
                            content = f.read()
                        marker = " Total Amount:"
                        if marker in content:
                            tail = content.split(marker, 1)[1]
                            amount_str = ""
                            for ch in tail:
                                if ch.isdigit() or ch in ".":
                                    amount_str += ch
                                elif amount_str:
                                    break
                            if amount_str:
                                sales_total += float(amount_str)
                    except:
                        continue
        except:
            pass

        # Update display
        try:
            self.emp_value.config(text=str(emp_total))
            self.pr_value.config(text=str(pr_total))
            self.sup_value.config(text=str(sup_total))
            self.sl_value.config(text=f"₱{sales_total:,.2f}")
        except:
            pass

    def collect_sales_by_date(self):
        """Collect sales data by date"""
        result = {}
        try:
            if os.path.isdir("bills"):
                for fname in os.listdir("bills"):
                    if not fname.endswith(".txt"):
                        continue
                    try:
                        with open(os.path.join("bills", fname), "r") as f:
                            content = f.read()

                        date_str = None
                        total_val = None

                        # Extract date
                        try:
                            parts = content.split("Date")
                            if len(parts) > 1:
                                line = parts[1]
                                segs = line.split(":")
                                if len(segs) >= 2:
                                    ds = segs[1].strip().split("  ")[0].strip()
                                    date_str = ds
                        except:
                            date_str = None

                        # Extract total
                        try:
                            marker = " Total Amount:"
                            if marker in content:
                                tail = content.split(marker, 1)[1]
                                amt = ""
                                for ch in tail:
                                    if ch.isdigit() or ch in ".":
                                        amt += ch
                                    elif amt:
                                        break
                                if amt:
                                    total_val = float(amt)
                        except:
                            total_val = None

                        if date_str and total_val is not None:
                            try:
                                d = datetime.strptime(date_str, "%d/%m/%Y").date()
                                key = d.isoformat()
                                result[key] = result.get(key, 0.0) + total_val
                            except:
                                pass
                    except:
                        continue
        except:
            pass
        return result

    def collect_sales_by_cashier(self, since_date=None):
        """Collect sales data by cashier"""
        totals = {}
        try:
            if os.path.isdir("bills"):
                for fname in os.listdir("bills"):
                    if not fname.endswith(".txt"):
                        continue
                    try:
                        with open(os.path.join("bills", fname), "r") as f:
                            content = f.read()

                        cashier = None
                        bill_date = None

                        # Extract cashier
                        try:
                            for line in content.splitlines():
                                if "Cashier" in line:
                                    parts = line.split(":")
                                    if len(parts) >= 2:
                                        name = parts[1].strip()
                                        if name:
                                            cashier = name
                                            break
                        except:
                            cashier = None

                        # Extract date
                        try:
                            for line in content.splitlines():
                                if "Date" in line and "Time" in line:
                                    segs = line.split(":")
                                    if len(segs) >= 2:
                                        ds = segs[1].strip().split("  ")[0].strip()
                                        bill_date = datetime.strptime(ds, "%d/%m/%Y").date()
                                        break
                        except:
                            bill_date = None

                        # Extract total
                        total_val = None
                        try:
                            marker = " Total Amount:"
                            if marker in content:
                                tail = content.split(marker, 1)[1]
                                amt = ""
                                for ch in tail:
                                    if ch.isdigit() or ch in ".":
                                        amt += ch
                                    elif amt:
                                        break
                                if amt:
                                    total_val = float(amt)
                        except:
                            total_val = None

                        if cashier and total_val is not None:
                            if since_date and bill_date:
                                if bill_date < since_date:
                                    continue
                            totals[cashier] = totals.get(cashier, 0.0) + total_val
                    except:
                        continue
        except:
            pass
        return totals

    def draw_sales_graph(self, period_days=30):
        """Draw sales graph"""
        self.graph_canvas.delete("all")
        data_map = self.collect_sales_by_date()
        today = date.today()
        days = [today - timedelta(days=i) for i in range(period_days - 1, -1, -1)]
        labels = [d.isoformat() for d in days]
        values = [data_map.get(l, 0.0) for l in labels]
        w = int(self.graph_canvas["width"])
        h = int(self.graph_canvas["height"])
        pad_left = 50
        pad_bottom = 30
        pad_top = 20
        pad_right = 10
        gx0 = pad_left
        gy0 = pad_top
        gx1 = w - pad_right
        gy1 = h - pad_bottom
        self.graph_canvas.create_rectangle(gx0, gy0, gx1, gy1, outline="#cccccc")
        max_val = max(values) if values else 0.0

        if max_val <= 0:
            self.graph_canvas.create_text((w // 2), (h // 2), text="No sales data", fill="#0a3e34",
                                          font=("Garamond", 12, "bold"))
            return

        bar_count = len(values)
        bar_space = (gx1 - gx0) / bar_count
        bar_w = max(2, bar_space * 0.6)

        for i, v in enumerate(values):
            x_center = gx0 + i * bar_space + bar_space / 2
            bar_h = 0
            try:
                bar_h = (v / max_val) * (gy1 - gy0)
            except:
                bar_h = 0
            x0 = x_center - bar_w / 2
            y0 = gy1 - bar_h
            x1 = x_center + bar_w / 2
            y1 = gy1
            self.graph_canvas.create_rectangle(x0, y0, x1, y1, fill="#0a3e34", outline="")
            if i % 5 == 0:
                self.graph_canvas.create_text(x_center, gy1 + 12, text=days[i].strftime("%m-%d"), fill="#555555",
                                              font=("Garamond", 8))

        # y-axis labels
        self.graph_canvas.create_text(pad_left - 10, gy1, text="0", fill="#555555", font=("Garamond", 8), anchor="e")
        self.graph_canvas.create_text(pad_left - 10, (gy0 + gy1) // 2, text=f"{max_val / 2:,.0f}", fill="#555555",
                                      font=("Garamond", 8), anchor="e")
        self.graph_canvas.create_text(pad_left - 10, gy0, text=f"{max_val:,.0f}", fill="#555555", font=("Garamond", 8),
                                      anchor="e")

    def draw_cashier_graph(self, since_date=None):
        """Draw cashier sales graph"""
        self.graph_canvas.delete("all")
        data_map = self.collect_sales_by_cashier(since_date=since_date)
        items = sorted(data_map.items(), key=lambda x: x[1], reverse=True)
        labels = [k for k, _ in items]
        values = [v for _, v in items]
        w = int(self.graph_canvas["width"])
        h = int(self.graph_canvas["height"])
        pad_left = 60
        pad_bottom = 50
        pad_top = 20
        pad_right = 10
        gx0 = pad_left
        gy0 = pad_top
        gx1 = w - pad_right
        gy1 = h - pad_bottom
        self.graph_canvas.create_rectangle(gx0, gy0, gx1, gy1, outline="#cccccc")
        max_val = max(values) if values else 0.0

        if not items or max_val <= 0:
            self.graph_canvas.create_text((w // 2), (h // 2), text="No cashier sales data", fill="#0a3e34",
                                          font=("Garamond", 12, "bold"))
            return

        bar_count = len(values)
        bar_space = (gx1 - gx0) / bar_count
        bar_w = max(8, bar_space * 0.6)

        for i, v in enumerate(values):
            x_center = gx0 + i * bar_space + bar_space / 2
            bar_h = 0
            try:
                bar_h = (v / max_val) * (gy1 - gy0)
            except:
                bar_h = 0
            x0 = x_center - bar_w / 2
            y0 = gy1 - bar_h
            x1 = x_center + bar_w / 2
            y1 = gy1
            self.graph_canvas.create_rectangle(x0, y0, x1, y1, fill="#0a3e34", outline="")
            self.graph_canvas.create_text(x_center, y0 - 12, text=f"₱{v:,.0f}", fill="#333333",
                                          font=("Garamond", 9, "bold"))
            name = labels[i]
            if len(name) > 14:
                name = name[:14] + "…"
            self.graph_canvas.create_text(x_center, gy1 + 20, text=name, fill="#555555", font=("Garamond", 9),
                                          anchor="n")

    def refresh_graph(self):
        """Refresh graph display"""
        mode = self.graph_mode_var.get()
        period = self.graph_period_var.get()
        days_map = {"7 days": 7, "30 days": 30, "90 days": 90}
        period_days = days_map.get(period, 30)

        if mode == "Cashiers":
            self.graph_title.config(text="Cashier Total Sales")
            since = date.today() - timedelta(days=period_days)
            self.draw_cashier_graph(since_date=since)
        else:
            self.graph_title.config(text=f"Daily Sales (last {period_days} days)")
            self.draw_sales_graph(period_days=period_days)

    def open_employee_form(self):
        """Open employee management form"""
        EmployeeForm(self.root)

    def open_supplier_form(self):
        """Open supplier management form"""
        SupplierForm(self.root)

    def open_product_form(self):
        """Open product management form"""
        ProductForm(self.root)

    def open_sales_form(self):
        """Open sales management form"""
        SalesForm(self.root)

    def open_cashier_window(self):
        """Open cashier in new window"""
        top = Toplevel(self.root)
        cashier_app = CashierClass(top, self.emp_id)

    def logout(self):
        """Handle logout"""
        self.root.destroy()
        login_root = Tk()
        login_app = LoginClass(login_root)
        login_root.mainloop()


# ================= CASHIER CLASS =================
class CashierClass:
    def __init__(self, root, emp_id):
        self.root = root
        self.root.geometry("1500x768+10+5")
        self.root.title("Grocery Cashier System")
        self.root.config(bg='white')
        self.root.resizable(False, False)

        # Variables
        self.emp_id = emp_id
        self.cashier_name = self.get_cashier_name(self.emp_id)
        self.var_pid = StringVar()
        self.var_pname = StringVar()
        self.var_price = DoubleVar()
        self.var_qty = IntVar()
        self.var_stock = StringVar()
        self.var_search = StringVar()
        self.var_cname = StringVar()
        self.var_ccontact = StringVar()
        self.cart_list = []
        self.var_total_bill = DoubleVar()
        self.var_total_bill.set(0.0)
        self.bill_no = ""

        # Create UI
        self.create_cashier_ui()

        # Initialize data
        self.fetch_products()
        self.update_time()

    def get_cashier_name(self, emp_id):
        """Get cashier name from database"""
        if not emp_id:
            return "Unknown Cashier"
        conn = None
        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("SELECT FirstName, LastName FROM employees WHERE EmpID=%s AND Role='Cashier'", (emp_id,))
            result = cur.fetchone()
            if result:
                return f"{result[0]} {result[1]}"
            else:
                return "Unknown Cashier"
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
            return "Error"
        finally:
            if conn:
                conn.close()

    def create_cashier_ui(self):
        """Create cashier interface"""
        # Title section
        titleLabel = Label(self.root, text="Grocery Sales & Inventory Management System",
                           font=('Garamond', 25, 'bold'), fg="white", bg="#0a3e34",
                           anchor='center', padx=10, pady=10)
        titleLabel.place(x=0, y=0, height=100, relwidth=1)

        # Date/Time/User Sub-label
        self.subLabel = Label(self.root, text="", font=('Garamond', 12, 'bold'), bg="#e9e6d5", fg="#0a3e34")
        self.subLabel.place(x=0, y=100, height=30, relwidth=1)

        # Logout Button
        logout_btn = Button(self.root, text="Logout", font=('Garamond', 15, 'bold'),
                            fg='#0a3e34', bg='#e9e6d5', cursor="hand2", command=self.logout)
        logout_btn.place(x=1350, y=30)

        # Left Frame (Search Area)
        self.leftFrame = Frame(self.root, bd=2, relief=RIDGE, bg="white")
        self.leftFrame.place(x=10, y=140, width=450, height=120)

        lbl_search = Label(self.leftFrame, text="Search Product By Name:", font=("Garamond", 12, "bold"),
                           bg="white", fg="#0a3e34")
        lbl_search.place(x=10, y=10)

        txt_search = Entry(self.leftFrame, textvariable=self.var_search, font=("Garamond", 15), bg="#e9e6d5")
        txt_search.place(x=10, y=40, width=280, height=30)

        btn_search = Button(self.leftFrame, text="Search", command=self.search_product,
                            font=("Garamond", 12, "bold"), bg="#0a3e34", fg="white", cursor="hand2")
        btn_search.place(x=300, y=40, width=130, height=30)

        btn_show_all = Button(self.leftFrame, text="Show All Available", command=self.fetch_products,
                              font=("Garamond", 12, "bold"), bg="#555", fg="white", cursor="hand2")
        btn_show_all.place(x=10, y=80, width=420, height=30)

        # Bottom Left Frame (Product Table)
        self.botFrame = Frame(self.root, bd=2, relief=RIDGE, bg="white")
        self.botFrame.place(x=10, y=270, width=450, height=480)

        scrolly = Scrollbar(self.botFrame, orient=VERTICAL)
        self.product_table = ttk.Treeview(self.botFrame, columns=("pid", "name", "price", "qty", "status"),
                                          yscrollcommand=scrolly.set)

        scrolly.pack(side=RIGHT, fill=Y)
        scrolly.config(command=self.product_table.yview)

        self.product_table.heading("pid", text="ID")
        self.product_table.heading("name", text="Name")
        self.product_table.heading("price", text="Price")
        self.product_table.heading("qty", text="Stock")
        self.product_table.heading("status", text="Status")

        self.product_table.column("pid", width=40)
        self.product_table.column("name", width=140)
        self.product_table.column("price", width=70)
        self.product_table.column("qty", width=60)
        self.product_table.column("status", width=80)

        self.product_table["show"] = "headings"
        self.product_table.pack(fill=BOTH, expand=1)
        self.product_table.bind("<ButtonRelease-1>", self.get_data)

        # Middle Frame (Customer, Calculator, Cart)
        self.middleFrame = Frame(self.root, bd=2, relief=RIDGE, bg="white")
        self.middleFrame.place(x=470, y=140, width=520, height=610)

        self.create_middle_frame_content()

        # Right Frame (Billing Area)
        self.rightFrame = Frame(self.root, bd=2, relief=RIDGE, bg="white")
        self.rightFrame.place(x=1000, y=140, width=480, height=610)

        self.create_billing_area()

    def create_middle_frame_content(self):
        """Create middle frame content"""
        # Customer Details
        lbl_m_title = Label(self.middleFrame, text="Customer Details", font=("Garamond", 15, "bold"),
                            bg="#0a3e34", fg="white")
        lbl_m_title.pack(side=TOP, fill=X)

        cust_frame = Frame(self.middleFrame, bg="white")
        cust_frame.pack(fill=X, pady=5)

        Label(cust_frame, text="Name:", font=("Garamond", 10, "bold"), bg="white").grid(row=0, column=0, padx=5,
                                                                                        sticky=W)
        Entry(cust_frame, textvariable=self.var_cname, font=("Garamond", 10), bg="#e9e6d5", width=20).grid(row=0,
                                                                                                           column=1,
                                                                                                           padx=5)

        Label(cust_frame, text="Contact:", font=("Garamond", 10, "bold"), bg="white").grid(row=0, column=2, padx=5,
                                                                                           sticky=W)
        Entry(cust_frame, textvariable=self.var_ccontact, font=("Garamond", 10), bg="#e9e6d5", width=20).grid(row=0,
                                                                                                              column=3,
                                                                                                              padx=5)

        # Calculator & Cart Area
        calc_cart_frame = Frame(self.middleFrame, bg="white")
        calc_cart_frame.pack(fill=BOTH, expand=True, pady=5)

        # Calculator
        self.calc_frame = Frame(calc_cart_frame, bd=2, relief=RIDGE, bg="#e9e6d5")
        self.calc_frame.place(x=5, y=0, width=240, height=270)

        self.calc_input = Entry(self.calc_frame, font=('Garamond', 15, 'bold'), width=18, justify=RIGHT)
        self.calc_input.grid(row=0, column=0, columnspan=4, padx=5, pady=5)

        btn_list = [
            '7', '8', '9', '+',
            '4', '5', '6', '-',
            '1', '2', '3', '*',
            'C', '0', '=', '/'
        ]

        r = 1
        c = 0
        for b in btn_list:
            cmd = lambda x=b: self.btn_click(x)
            Button(self.calc_frame, text=b, command=cmd, font=('Garamond', 12, 'bold'), width=4, height=2).grid(row=r,
                                                                                                                column=c,
                                                                                                                padx=2,
                                                                                                                pady=2)
            c += 1
            if c > 3:
                c = 0
                r += 1

        # Cart Table
        cart_frame = Frame(calc_cart_frame, bd=2, relief=RIDGE, bg="white")
        cart_frame.place(x=250, y=0, width=260, height=270)

        lbl_cart = Label(cart_frame, text="Cart / Purchase List", font=("Garamond", 12, "bold"), bg="#0a3e34",
                         fg="white")
        lbl_cart.pack(side=TOP, fill=X)

        scrolly_cart = Scrollbar(cart_frame, orient=VERTICAL)
        self.CartTable = ttk.Treeview(cart_frame, columns=("pname", "price", "qty"), yscrollcommand=scrolly_cart.set)
        scrolly_cart.pack(side=RIGHT, fill=Y)
        scrolly_cart.config(command=self.CartTable.yview)

        self.CartTable.heading("pname", text="Name")
        self.CartTable.heading("price", text="Price")
        self.CartTable.heading("qty", text="Qty")
        self.CartTable.column("pname", width=120)
        self.CartTable.column("price", width=60)
        self.CartTable.column("qty", width=40)
        self.CartTable["show"] = "headings"
        self.CartTable.pack(fill=BOTH, expand=1)
        self.CartTable.bind("<ButtonRelease-1>", self.get_cart_data)

        # Product Selection & Add to Cart
        prod_select_frame = Frame(self.middleFrame, bd=2, relief=RIDGE, bg="white")
        prod_select_frame.pack(side=BOTTOM, fill=X, pady=5)

        Label(prod_select_frame, text="Product Name", font=("Garamond", 10, "bold"), bg="white").grid(row=0, column=0,
                                                                                                      padx=5, pady=2)
        Entry(prod_select_frame, textvariable=self.var_pname, font=("Garamond", 10), bg="#e9e6d5", state='readonly',
              width=20).grid(row=0, column=1, padx=5, pady=2)

        Label(prod_select_frame, text="Price (PHP)", font=("Garamond", 10, "bold"), bg="white").grid(row=1, column=0,
                                                                                                     padx=5, pady=2)
        Entry(prod_select_frame, textvariable=self.var_price, font=("Garamond", 10), bg="#e9e6d5", state='readonly',
              width=20).grid(row=1, column=1, padx=5, pady=2)

        Label(prod_select_frame, text="Quantity", font=("Garamond", 10, "bold"), bg="white").grid(row=2, column=0,
                                                                                                  padx=5, pady=2)
        Entry(prod_select_frame, textvariable=self.var_qty, font=("Garamond", 10), bg="#e9e6d5", width=20).grid(row=2,
                                                                                                                column=1,
                                                                                                                padx=5,
                                                                                                                pady=2)

        Label(prod_select_frame, text="Stock Avail.", font=("Garamond", 10, "bold"), bg="white").grid(row=3, column=0,
                                                                                                      padx=5, pady=2)
        Entry(prod_select_frame, textvariable=self.var_stock, font=("Garamond", 10), bg="#e9e6d5", state='readonly',
              width=20).grid(row=3, column=1, padx=5, pady=2)

        # Buttons
        btn_prod_frame = Frame(prod_select_frame, bg="white")
        btn_prod_frame.grid(row=0, column=2, rowspan=4, padx=10)

        Button(btn_prod_frame, text="Add to Cart", command=self.add_cart, font=("Garamond", 12, "bold"), bg="#0a3e34",
               fg="white", width=12, height=2).pack(pady=2)
        Button(btn_prod_frame, text="Clear", command=self.clear_product_input, font=("Garamond", 12, "bold"), bg="#555",
               fg="white", width=12).pack(pady=2)

        lbl_inst = Label(self.middleFrame, text="Note: Select product from Left Table", font=("Garamond", 9), fg="red",
                         bg="white")
        lbl_inst.pack(side=BOTTOM)

    def create_billing_area(self):
        """Create billing area"""
        lbl_r_title = Label(self.rightFrame, text="Customer Receipt", font=("Garamond", 15, "bold"),
                            bg="#0a3e34", fg="white")
        lbl_r_title.pack(side=TOP, fill=X)

        self.txt_bill_area = Text(self.rightFrame, font=("courier new", 10))
        self.txt_bill_area.pack(fill=BOTH, expand=1)

        # Bill Buttons
        btn_bill_frame = Frame(self.rightFrame, bg="white")
        btn_bill_frame.pack(side=BOTTOM, fill=X)

        self.lbl_amnt = Label(btn_bill_frame, text="Total: 0.00 PHP", font=("Garamond", 14, "bold"), bg="white",
                              fg="#0a3e34")
        self.lbl_amnt.pack(fill=X, pady=5)

        Button(btn_bill_frame, text="Generate Bill", command=self.generate_bill, bg="#0a3e34", fg="white",
               font=("Garamond", 12, "bold"), width=15).pack(side=LEFT, padx=5, pady=10)
        Button(btn_bill_frame, text="Print & Save", command=self.print_bill, bg="#2196F3", fg="white",
               font=("Garamond", 12, "bold"), width=15).pack(side=LEFT, padx=5, pady=10)
        Button(btn_bill_frame, text="Clear All", command=self.clear_all, bg="#f44336", fg="white",
               font=("Garamond", 12, "bold"), width=10).pack(side=LEFT, padx=5, pady=10)

    def update_time(self):
        """Update time display"""
        current_date = date.today().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M:%S")
        self.subLabel.config(text=f"Welcome: {self.cashier_name}   |   Date: {current_date}   |   Time: {current_time}")
        self.subLabel.after(1000, self.update_time)

    def fetch_products(self):
        """Fetch products from database"""
        self.product_table.delete(*self.product_table.get_children())
        conn = None
        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute(
                "SELECT PrID, PrName, Price, Quantity, Availability FROM Product WHERE IsArchived=0 AND Availability='Available' AND Quantity > 0")
            rows = cur.fetchall()
            for row in rows:
                self.product_table.insert("", END, values=row)
        except Exception as ex:
            messagebox.showerror("Error", f"Database Error: {str(ex)}")
        finally:
            if conn:
                conn.close()

    def search_product(self):
        """Search products"""
        if self.var_search.get() == "":
            messagebox.showerror("Error", "Please enter product name to search")
            return

        self.product_table.delete(*self.product_table.get_children())
        conn = None
        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute(
                "SELECT PrID, PrName, Price, Quantity, Availability FROM Product WHERE PrName LIKE %s AND IsArchived=0 AND Quantity > 0",
                ('%' + self.var_search.get() + '%',))
            rows = cur.fetchall()
            if len(rows) != 0:
                for row in rows:
                    self.product_table.insert("", END, values=row)
            else:
                messagebox.showinfo("Not Found", "No available product found with that name")
        except Exception as ex:
            messagebox.showerror("Error", f"Database Error: {str(ex)}")
        finally:
            if conn:
                conn.close()

    def get_data(self, ev):
        """Get product data from table"""
        try:
            f = self.product_table.focus()
            content = (self.product_table.item(f))
            row = content['values']
            if row:
                self.var_pid.set(row[0])
                self.var_pname.set(row[1])
                self.var_price.set(row[2])
                self.var_qty.set(1)
                self.var_stock.set(row[3])
        except IndexError:
            pass

    def get_cart_data(self, ev):
        """Get cart data (optional implementation)"""
        pass

    def add_cart(self):
        """Add product to cart"""
        if self.var_pid.get() == "":
            messagebox.showerror("Error", "Please select a product from the list")
            return

        try:
            qty = self.var_qty.get()
            stock = int(self.var_stock.get())
            price = float(self.var_price.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid Format for Quantity or Stock")
            return

        if qty == 0:
            messagebox.showerror("Error", "Quantity cannot be zero")
            return

        if qty > stock:
            messagebox.showerror("Error", "Requested quantity exceeds available stock")
            return

        # Check if already in cart
        for item in self.cart_list:
            if item[0] == self.var_pid.get():
                messagebox.showerror("Error", "Product already in cart. Remove it to update quantity.")
                return

        total_price = price * qty
        self.cart_list.append([self.var_pid.get(), self.var_pname.get(), price, qty, total_price])

        # Add to Cart Treeview
        self.CartTable.insert("", END, values=(self.var_pname.get(), price, qty))
        self.update_total_bill()
        self.clear_product_input()
        messagebox.showinfo("Success", "Item Added to Cart")

    def update_total_bill(self):
        """Update total bill amount"""
        total = 0.0
        for item in self.cart_list:
            total += item[4]
        self.var_total_bill.set(total)
        self.lbl_amnt.config(text=f"Total: {str(total)} PHP")

    def clear_product_input(self):
        """Clear product input fields"""
        self.var_pid.set("")
        self.var_pname.set("")
        self.var_price.set("")
        self.var_qty.set(0)
        self.var_stock.set("")

    def generate_bill(self):
        """Generate bill"""
        if len(self.cart_list) == 0:
            messagebox.showerror("Error", "Cart is empty")
            return
        if self.var_cname.get() == "" or self.var_ccontact.get() == "":
            messagebox.showerror("Error", "Customer Details Required")
            return

        # Receipt Header
        self.bill_no = str(random.randint(1000, 9999))
        date_now = datetime.now().strftime("%d/%m/%Y")
        time_now = datetime.now().strftime("%H:%M:%S")

        self.txt_bill_area.delete('1.0', END)
        self.txt_bill_area.insert(END, "\t    GROCERY STORE RECEIPT\n")
        self.txt_bill_area.insert(END, "\t    Tel: +63 900 000 0000\n")
        self.txt_bill_area.insert(END, "------------------------------------------------\n")
        self.txt_bill_area.insert(END, f" Bill No : {self.bill_no}\n")
        self.txt_bill_area.insert(END, f" Date    : {date_now}  Time: {time_now}\n")
        self.txt_bill_area.insert(END, f" Cashier : {self.cashier_name}\n")
        self.txt_bill_area.insert(END, f" Customer: {self.var_cname.get()}\n")
        self.txt_bill_area.insert(END, f" Contact : {self.var_ccontact.get()}\n")
        self.txt_bill_area.insert(END, "------------------------------------------------\n")
        self.txt_bill_area.insert(END, " Product\t\tQty\tPrice\tTotal\n")
        self.txt_bill_area.insert(END, "------------------------------------------------\n")

        # Receipt Body
        for item in self.cart_list:
            name = item[1]
            qty = item[3]
            price = item[2]
            total = item[4]
            self.txt_bill_area.insert(END, f" {name}\t\t{qty}\t{price}\t{total}\n")

        self.txt_bill_area.insert(END, "------------------------------------------------\n")
        self.txt_bill_area.insert(END, f" Total Amount:\t\t\t\tPHP {self.var_total_bill.get()}\n")
        self.txt_bill_area.insert(END, "------------------------------------------------\n")
        self.txt_bill_area.insert(END, "\t  THANK YOU FOR SHOPPING!\n")

    def print_bill(self):
        """Print and save bill"""
        if len(self.cart_list) == 0:
            messagebox.showerror("Error", "Cart is empty")
            return
        if not self.bill_no:
            messagebox.showerror("Error", "Please Generate Bill First")
            return

        # Create bills folder if not exists
        if not os.path.exists("bills"):
            os.mkdir("bills")

        conn = None
        try:
            conn = connect_db()
            cur = conn.cursor()

            # Update Database Stock
            for item in self.cart_list:
                pid = item[0]
                qty_sold = item[3]

                # Get current stock to ensure accuracy
                cur.execute("SELECT Quantity FROM Product WHERE PrID=%s", (pid,))
                res = cur.fetchone()
                if res:
                    current_stock = res[0]
                    new_stock = current_stock - qty_sold

                    # Determine Status
                    status = "Available"
                    if new_stock <= 0:
                        new_stock = 0
                        status = "Out of Stock"

                    cur.execute("UPDATE Product SET Quantity=%s, Availability=%s WHERE PrID=%s",
                                (new_stock, status, pid))

            conn.commit()

            # Save to file only if DB update succeeds
            bill_content = self.txt_bill_area.get('1.0', END)
            with open(f"bills/{self.bill_no}.txt", "w") as f:
                f.write(bill_content)

            messagebox.showinfo("Success", f"Bill Saved as {self.bill_no}.txt and Stock Updated")
            self.clear_all()
            self.fetch_products()

        except Exception as ex:
            if conn:
                conn.rollback()
            messagebox.showerror("Error", f"Error Saving Bill: {str(ex)}")
        finally:
            if conn:
                conn.close()

    def clear_all(self):
        """Clear all fields"""
        self.cart_list = []
        self.var_cname.set("")
        self.var_ccontact.set("")
        self.var_total_bill.set(0.0)
        self.bill_no = ""
        self.lbl_amnt.config(text="Total: 0.00 PHP")
        self.clear_product_input()
        self.CartTable.delete(*self.CartTable.get_children())
        self.txt_bill_area.delete('1.0', END)
        self.calc_input.delete(0, END)

    def btn_click(self, char):
        """Calculator button click handler"""
        if char == 'C':
            self.calc_input.delete(0, END)
        elif char == '=':
            try:
                result = str(eval(self.calc_input.get()))
                self.calc_input.delete(0, END)
                self.calc_input.insert(0, result)
            except:
                self.calc_input.delete(0, END)
                self.calc_input.insert(0, "Error")
        else:
            self.calc_input.insert(END, char)

    def logout(self):
        """Handle logout"""
        self.root.destroy()
        login_root = Tk()
        login_app = LoginClass(login_root)
        login_root.mainloop()


# ================= EMPLOYEE FORM CLASS =================
class EmployeeForm:
    def __init__(self, parent_window):
        self.parent = parent_window

        # Create employee frame
        self.empl_Frame = Frame(parent_window, width=1400, height=608, bg="#e9e6d5")
        self.empl_Frame.place(x=200, y=150)

        Label(self.empl_Frame, text="Employee Management", font=('Garamond', 16, 'bold'), bg="#e9e6d5",
              fg="#0a3e34").place(x=0, y=0, relwidth=1, height=40)

        Button(self.empl_Frame, text="Back", font=('Garamond', 10, 'bold'), cursor='hand2', bg="#e9e6d5", fg="#0a3e34",
               command=self.close_form).place(x=10, y=50)

        # Labels for employee fields
        self.labels = [
            "Employee ID", "First Name", "Last Name", "Email", "Gender",
            "Date of Birth", "Contact No", "Employee Type", "Education",
            "Address", "Date of Joining", "Salary", "Role", "Password"
        ]
        self.entries = {}

        self.create_employee_ui()
        self.show_all_db()

    def create_employee_ui(self):
        """Create employee management interface"""
        # Top frame with search and table
        topFrame = Frame(self.empl_Frame, bg='white')
        topFrame.place(x=0, y=90, relwidth=1, height=235)

        searchFrame = Frame(topFrame)
        searchFrame.pack()

        self.search_comboB = ttk.Combobox(searchFrame, values=('ID', 'Name', 'Email'), font=('Garamond', 12, 'bold'),
                                          state='readonly')
        self.search_comboB.set('Search By')
        self.search_comboB.grid(column=0, row=0, padx=20)

        self.search_entry = Entry(searchFrame, font=('Garamond', 12, 'bold'), bg='#e9e6d5')
        self.search_entry.grid(column=1, row=0)

        # Treeview
        tree_frame = Frame(topFrame)
        tree_frame.pack(pady=10, fill="both", expand=True)

        scroll_y = ttk.Scrollbar(tree_frame, orient="vertical")
        scroll_y.pack(side="right", fill="y")
        scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal")
        scroll_x.pack(side="bottom", fill="x")

        self.emp_tree = ttk.Treeview(tree_frame, columns=self.labels, show='headings', yscrollcommand=scroll_y.set,
                                     xscrollcommand=scroll_x.set)
        self.emp_tree.pack(fill="both", expand=True)
        scroll_y.config(command=self.emp_tree.yview)
        scroll_x.config(command=self.emp_tree.xview)

        for col in self.labels:
            self.emp_tree.heading(col, text=col)
            self.emp_tree.column(col, width=150)

        # Form frame
        formFrame = Frame(self.empl_Frame, bg="white")
        formFrame.place(x=0, y=330, relwidth=1, height=278)

        row, col = 0, 0
        for index, label_text in enumerate(self.labels):
            Label(formFrame, text=label_text, font=('Garamond', 12, 'bold'), bg="white").grid(row=row, column=col,
                                                                                              padx=50, pady=10,
                                                                                              sticky="w")

            if label_text == "Gender":
                entry = ttk.Combobox(formFrame, font=('Garamond', 12), values=["Male", "Female"], state="readonly",
                                     width=18)
                entry.set('Gender')
            elif label_text == "Employee Type":
                entry = ttk.Combobox(formFrame, font=('Garamond', 12), values=["Regular", "Part-Time", "Contract"],
                                     state="readonly", width=18)
                entry.set('Employee Type')
            elif label_text == "Role":
                entry = ttk.Combobox(formFrame, font=('Garamond', 12), values=["Admin", "Cashier"], state="readonly",
                                     width=18)
                entry.set('Role')
            elif label_text in ["Date of Birth", "Date of Joining"]:
                entry = DateEntry(formFrame, width=18, font=('Garamond', 12), background="#aada8e",
                                  foreground="#e9e6d5", date_pattern="yyyy-mm-dd")
            else:
                entry = Entry(formFrame, width=20, font=('Garamond', 12), bg='#e9e6d5')

            entry.grid(row=row, column=col + 1, padx=20, pady=10)
            self.entries[label_text] = entry

            col += 2
            if col > 4:
                col = 0
                row += 1

        # Buttons
        btnFrame = Frame(formFrame, bg="white")
        btnFrame.grid(row=row + 1, column=0, columnspan=6, pady=20)

        Button(btnFrame, text="Add Employee", width=15, bg="#0a3e34", fg="white", font=('Garamond', 12, 'bold'),
               command=self.add_employee_db).grid(row=0, column=0, padx=10)
        Button(btnFrame, text="Update", width=15, bg="#0a3e34", fg="white", font=('Garamond', 12, 'bold'),
               command=self.update_employee_db).grid(row=0, column=1, padx=10)
        Button(btnFrame, text="Delete", width=15, bg="#a30000", fg="white", font=('Garamond', 12, 'bold'),
               command=self.delete_employee_db).grid(row=0, column=2, padx=10)
        Button(btnFrame, text="Clear", width=15, bg="#444444", fg="white", font=('Garamond', 12, 'bold'),
               command=self.clear_entries).grid(row=0, column=3, padx=10)

        Button(searchFrame, text="Search", width=10, fg='#e9e6d5', bg='#0a3e34', font=('Garamond', 12, 'bold'),
               command=self.search_employee_db).grid(column=2, row=0, padx=20)
        Button(searchFrame, text="Show All", width=10, fg='#e9e6d5', bg='#0a3e34', font=('Garamond', 12, 'bold'),
               command=self.show_all_db).grid(column=3, row=0, padx=20)
        Button(searchFrame, text="Archive", width=12, fg='#e9e6d5', bg='#0a3e34', font=('Garamond', 12, 'bold'),
               command=self.show_archived_db).grid(column=4, row=0, padx=10)
        Button(searchFrame, text="Revive", width=12, fg='#e9e6d5', bg='#0a3e34', font=('Garamond', 12, 'bold'),
               command=self.revive_employee_db).grid(column=5, row=0, padx=10)

        self.emp_tree.bind("<<TreeviewSelect>>", self.fill_form_from_treeview)

    def clear_entries(self):
        """Clear all entry fields"""
        for label in self.labels:
            if isinstance(self.entries[label], ttk.Combobox):
                self.entries[label].set("")
            else:
                self.entries[label].delete(0, END)

    def fill_form_from_treeview(self, event):
        """Fill form from selected treeview item"""
        selected = self.emp_tree.focus()
        if not selected:
            return
        values = self.emp_tree.item(selected, "values")
        for i, label in enumerate(self.labels):
            if isinstance(self.entries[label], ttk.Combobox):
                self.entries[label].set(values[i])
            else:
                self.entries[label].delete(0, END)
                self.entries[label].insert(0, values[i])

    def add_employee_db(self):
        """Add employee to database"""
        try:
            conn = connect_db()
            cur = conn.cursor()
            values = [self.entries[label].get() for label in self.labels]
            sql = """INSERT INTO employees
            (EmpID, FirstName, LastName, Email, Gender, DOB, ContactNo,
             EmpType, Education, Address, DOJ, Salary, Role, Password)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            cur.execute(sql, values)
            conn.commit()
            messagebox.showinfo("Success", "Employee added successfully!")
            self.show_all_db()
            self.clear_entries()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", err)
        finally:
            cur.close()
            conn.close()

    def update_employee_db(self):
        """Update employee in database"""
        selected = self.emp_tree.focus()
        if not selected:
            messagebox.showwarning("Select Row", "Select a record to update.")
            return
        try:
            conn = connect_db()
            cur = conn.cursor()
            values = [self.entries[label].get() for label in self.labels]
            sql = """UPDATE employees SET
                        FirstName=%s, LastName=%s, Email=%s, Gender=%s, DOB=%s,
                        ContactNo=%s, EmpType=%s, Education=%s, Address=%s,
                        DOJ=%s, Salary=%s, Role=%s, Password=%s
                     WHERE EmpID=%s"""
            update_values = values[1:] + [values[0]]
            cur.execute(sql, update_values)
            conn.commit()
            messagebox.showinfo("Updated", "Employee record updated!")
            self.show_all_db()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", err)
        finally:
            cur.close()
            conn.close()

    def delete_employee_db(self):
        """Archive employee"""
        selected = self.emp_tree.focus()
        if not selected:
            messagebox.showwarning("Select Row", "Select a record first.")
            return
        emp_id = self.emp_tree.item(selected, "values")[0]
        if not messagebox.askyesno("Confirm", "Archive this employee?"):
            return
        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("UPDATE employees SET Archived=1 WHERE EmpID=%s", (emp_id,))
            conn.commit()
            self.emp_tree.delete(selected)
            messagebox.showinfo("Archived", "Employee archived successfully.")
            self.clear_entries()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", err)
        finally:
            cur.close()
            conn.close()

    def show_all_db(self):
        """Show all employees"""
        for row in self.emp_tree.get_children():
            self.emp_tree.delete(row)
        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("SELECT * FROM employees WHERE Archived=0")
            rows = cur.fetchall()
            for row in rows:
                self.emp_tree.insert("", END, values=row)
        except mysql.connector.Error as err:
            messagebox.showerror("Error", err)
        finally:
            cur.close()
            conn.close()

    def show_archived_db(self):
        """Show archived employees"""
        for row in self.emp_tree.get_children():
            self.emp_tree.delete(row)
        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("SELECT * FROM employees WHERE Archived=1")
            rows = cur.fetchall()
            for row in rows:
                self.emp_tree.insert("", END, values=row)
        except mysql.connector.Error as err:
            messagebox.showerror("Error", err)
        finally:
            cur.close()
            conn.close()

    def revive_employee_db(self):
        """Revive archived employee"""
        selected = self.emp_tree.focus()
        if not selected:
            messagebox.showwarning("Select Row", "Select a record first.")
            return
        emp_id = self.emp_tree.item(selected, "values")[0]
        if not messagebox.askyesno("Confirm", "Restore this employee?"):
            return
        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("UPDATE employees SET Archived=0 WHERE EmpID=%s", (emp_id,))
            conn.commit()
            self.emp_tree.delete(selected)
            messagebox.showinfo("Restored", "Employee restored successfully.")
            self.show_archived_db()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", err)
        finally:
            cur.close()
            conn.close()

    def search_employee_db(self):
        """Search employees"""
        field = self.search_comboB.get()
        value = self.search_entry.get().strip()
        if field == "Search By" or value == "":
            messagebox.showwarning("Input Needed", "Choose a field and enter value")
            return
        db_field = {"ID": "EmpID", "Name": "FirstName", "Email": "Email"}[field]
        for row in self.emp_tree.get_children():
            self.emp_tree.delete(row)
        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute(f"SELECT * FROM employees WHERE {db_field} LIKE %s", (f"%{value}%",))
            rows = cur.fetchall()
            for row in rows:
                self.emp_tree.insert("", END, values=row)
        except mysql.connector.Error as err:
            messagebox.showerror("Error", err)
        finally:
            cur.close()
            conn.close()

    def close_form(self):
        """Close employee form"""
        self.empl_Frame.place_forget()


# ================= SUPPLIER FORM CLASS =================
class SupplierForm:
    def __init__(self, parent_window):
        self.parent = parent_window

        # Create supplier frame
        self.supframe = Frame(parent_window, width=1400, height=608, bg="#e9e6d5")
        self.supframe.place(x=200, y=150)

        Label(self.supframe, text="Supplier Management", font=('Garamond', 16, 'bold'), bg="#e9e6d5",
              fg="#0a3e34").place(x=0, y=0, relwidth=1, height=40)
        Button(self.supframe, text="Back", font=('Garamond', 10, 'bold'), cursor='hand2', bg="#e9e6d5", fg="#0a3e34",
               command=self.close_form).place(x=10, y=50)

        self.create_supplier_ui()
        self.load_suppliers()

    def create_supplier_ui(self):
        """Create supplier management interface"""
        # Entry fields
        Label(self.supframe, text="Invoice No.", font=('Garamond', 12, 'bold'), bg='#e9e6d5').place(x=20, y=90)
        self.invoice_entry = Entry(self.supframe, bg="white")
        self.invoice_entry.place(x=140, y=95, width=200)

        Label(self.supframe, text="Supplier Name", font=('Garamond', 12, 'bold'), bg='#e9e6d5').place(x=20, y=130)
        self.name_entry = Entry(self.supframe, bg="white")
        self.name_entry.place(x=140, y=135, width=200)

        Label(self.supframe, text="Contact", font=('Garamond', 12, 'bold'), bg='#e9e6d5').place(x=20, y=170)
        self.contact_entry = Entry(self.supframe, bg="white")
        self.contact_entry.place(x=140, y=175, width=200)

        Label(self.supframe, text="Description", font=('Garamond', 12, 'bold'), bg='#e9e6d5').place(x=20, y=210)
        self.desc_entry = Text(self.supframe, bg="white")
        self.desc_entry.place(x=140, y=215, width=300, height=130)

        # Buttons
        Button(self.supframe, text="Save", font=('Garamond', 12, 'bold'), bg="#0a3e34", fg="white",
               command=self.save_supplier).place(x=20, y=370, width=90)
        Button(self.supframe, text="Update", font=('Garamond', 12, 'bold'), bg="#0a3e34", fg="white",
               command=self.update_supplier).place(x=130, y=370, width=90)
        Button(self.supframe, text="Delete", font=('Garamond', 12, 'bold'), bg="#a30000", fg="white",
               command=self.delete_supplier).place(x=240, y=370, width=90)
        Button(self.supframe, text="Clear", font=('Garamond', 12, 'bold'), bg="#444444", fg="white",
               command=self.clear_fields).place(x=350, y=370, width=90)
        Button(self.supframe, text="Revive", font=('Garamond', 12, 'bold'), bg="#0a3e34", fg="white",
               command=self.revive_supplier).place(x=460, y=370, width=90)

        # Search area
        Label(self.supframe, text="Invoice No", font=('Garamond', 12, 'bold'), bg="#e9e6d5").place(x=530, y=90)
        self.search_entry = Entry(self.supframe, bg="white")
        self.search_entry.place(x=630, y=90, width=200)

        Button(self.supframe, text="Search", font=('Garamond', 12, 'bold'), bg="#0a3e34", fg="white",
               command=self.search_supplier).place(x=850, y=85, width=90)
        Button(self.supframe, text="Show All", font=('Garamond', 12, 'bold'), bg="#0a3e34", fg="white",
               command=self.show_all_suppliers).place(x=960, y=85, width=90)
        Button(self.supframe, text="Archived", font=('Garamond', 12, 'bold'), bg="#0a3e34", fg="white",
               command=self.show_archived_suppliers).place(x=1070, y=85, width=90)

        # Treeview
        tree_frame = Frame(self.supframe, bg="white", bd=2, relief=RIDGE)
        tree_frame.place(x=550, y=130, width=630, height=380)

        self.tree = ttk.Treeview(tree_frame, columns=("SupID", "InvoiceNo", "Name", "Contact", "Description"),
                                 show="headings")

        for col, w in zip(self.tree["columns"], [60, 120, 150, 120, 200]):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w)

        self.tree.pack(fill=BOTH, expand=1)
        self.tree.bind("<ButtonRelease-1>", self.populate_fields)

    def clear_fields(self):
        """Clear all fields"""
        self.invoice_entry.delete(0, END)
        self.name_entry.delete(0, END)
        self.contact_entry.delete(0, END)
        self.desc_entry.delete("1.0", END)
        self.tree.selection_remove(self.tree.selection())

    def load_suppliers(self):
        """Load suppliers from database"""
        self.tree.delete(*self.tree.get_children())
        db = connect_db()
        cur = db.cursor()
        cur.execute("SELECT SupID, InvoiceNo, Name, Contact, Description FROM Supplier WHERE IsArchived = 0")
        for row in cur.fetchall():
            self.tree.insert("", END, values=row)
        db.close()

    def save_supplier(self):
        """Save supplier to database"""
        if not self.invoice_entry.get() or not self.name_entry.get():
            messagebox.showwarning("Input Error", "Invoice No and Name are required")
            return

        db = connect_db()
        cur = db.cursor()
        cur.execute(
            """INSERT INTO Supplier (InvoiceNo, Name, Contact, Description, IsArchived) VALUES (%s, %s, %s, %s, 0)""", (
                self.invoice_entry.get(),
                self.name_entry.get(),
                self.contact_entry.get(),
                self.desc_entry.get("1.0", END).strip()
            ))
        db.commit()
        db.close()

        self.clear_fields()
        self.load_suppliers()
        messagebox.showinfo("Success", "Supplier saved")

    def update_supplier(self):
        """Update supplier in database"""
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Select", "Select a supplier to update")
            return

        sup_id = self.tree.item(selected)['values'][0]

        db = connect_db()
        cur = db.cursor()
        cur.execute("""UPDATE Supplier SET InvoiceNo=%s, Name=%s, Contact=%s, Description=%s WHERE SupID=%s""", (
            self.invoice_entry.get(),
            self.name_entry.get(),
            self.contact_entry.get(),
            self.desc_entry.get("1.0", END).strip(),
            sup_id
        ))
        db.commit()
        db.close()

        self.clear_fields()
        self.load_suppliers()
        messagebox.showinfo("Updated", "Supplier updated")

    def delete_supplier(self):
        """Archive supplier"""
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Select", "Select a supplier to archive")
            return

        sup_id = self.tree.item(selected)['values'][0]

        db = connect_db()
        cur = db.cursor()
        cur.execute("UPDATE Supplier SET IsArchived=1 WHERE SupID=%s", (sup_id,))
        db.commit()
        db.close()

        self.clear_fields()
        self.load_suppliers()
        messagebox.showinfo("Archived", "Supplier archived")

    def revive_supplier(self):
        """Revive archived supplier"""
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Select", "Select a supplier to revive.")
            return

        sup_id = self.tree.item(selected)['values'][0]

        db = connect_db()
        cur = db.cursor()
        cur.execute("UPDATE Supplier SET IsArchived=0 WHERE SupID=%s", (sup_id,))
        db.commit()
        db.close()

        self.load_suppliers()
        self.clear_fields()
        messagebox.showinfo("Restored", "Supplier restored successfully.")

    def search_supplier(self):
        """Search suppliers"""
        self.tree.delete(*self.tree.get_children())
        db = connect_db()
        cur = db.cursor()
        cur.execute(
            """SELECT SupID, InvoiceNo, Name, Contact, Description FROM Supplier WHERE InvoiceNo LIKE %s AND IsArchived = 0""",
            ('%' + self.search_entry.get() + '%',))
        for row in cur.fetchall():
            self.tree.insert("", END, values=row)
        db.close()

    def show_archived_suppliers(self):
        """Show archived suppliers"""
        self.tree.delete(*self.tree.get_children())
        db = connect_db()
        cur = db.cursor()
        cur.execute("""SELECT SupID, InvoiceNo, Name, Contact, Description FROM Supplier WHERE IsArchived = 1""")
        for row in cur.fetchall():
            self.tree.insert("", END, values=row)
        db.close()

    def show_all_suppliers(self):
        """Show all suppliers"""
        self.load_suppliers()

    def populate_fields(self, event):
        """Populate fields from selected item"""
        selected = self.tree.focus()
        if not selected:
            return
        vals = self.tree.item(selected)['values']
        self.invoice_entry.delete(0, END)
        self.invoice_entry.insert(0, vals[1])
        self.name_entry.delete(0, END)
        self.name_entry.insert(0, vals[2])
        self.contact_entry.delete(0, END)
        self.contact_entry.insert(0, vals[3])
        self.desc_entry.delete("1.0", END)
        self.desc_entry.insert(END, vals[4])

    def close_form(self):
        """Close supplier form"""
        self.supframe.place_forget()


# ================= PRODUCT FORM CLASS =================
class ProductForm:
    def __init__(self, parent_window):
        self.parent = parent_window

        # Create product frame
        self.prodFrame = Frame(parent_window, width=1400, height=608, bg="#e9e6d5")
        self.prodFrame.place(x=200, y=150)

        Label(self.prodFrame, text="Product Management", font=('Garamond', 16, 'bold'), bg="#e9e6d5",
              fg="#0a3e34").place(x=0, y=0, relwidth=1, height=40)
        Button(self.prodFrame, text="Back", font=('Garamond', 10, 'bold'), cursor='hand2', bg="#e9e6d5", fg="#0a3e34",
               command=self.close_form).place(x=10, y=50)

        # Variables
        self.selected_id = StringVar()
        self.prname_var = StringVar()
        self.brand_var = StringVar()
        self.category_var = StringVar()
        self.price_var = StringVar()
        self.quantity_var = StringVar()
        self.availability_var = StringVar()
        self.shelf_var = StringVar()
        self.supplier_var = StringVar()
        self.search_by_var = StringVar()
        self.search_var = StringVar()

        self.create_product_ui()
        self.load_suppliers()
        self.show_all()

    def create_product_ui(self):
        """Create product management interface"""
        # Manage frame
        manageFrame = LabelFrame(self.prodFrame, text="Manage Product Details", font=('Garamond', 14, 'bold'),
                                 bg="white", padx=30, pady=10)
        manageFrame.place(x=20, y=90, width=600, height=500)

        # Product fields
        fields = [("Product Name:", self.prname_var), ("Brand:", self.brand_var)]
        for i, (lbl, var) in enumerate(fields):
            Label(manageFrame, text=lbl, font=('Garamond', 12), bg='white').grid(row=i, column=0, sticky=W, pady=5)
            Entry(manageFrame, textvariable=var, background='#e9e6d5').grid(row=i, column=1, pady=5)

        row = 2
        Label(manageFrame, text="Category:", font=('Garamond', 12), bg='white').grid(row=row, column=0, sticky=W,
                                                                                     pady=5)
        ttk.Combobox(manageFrame, textvariable=self.category_var, values=[
            "Rice and Grains", "Canned and Packaged Goods", "Beverages", "Snacks and Sweets", "Dairy Products",
            "Meat and Poultry", "Seafood", "Fruits", "Vegetables", "Frozen Foods", "Bread and Bakery",
            "Condiments and Sauces", "Cooking Oil and Spices", "Instant Noodles and Ready Meals",
            "Household Cleaning Supplies", "Personal Care and Hygiene", "Baby Products"
        ], width=13, font=('Garamond', 12), background='#e9e6d5').grid(row=row, column=1, pady=5)

        row += 1
        Label(manageFrame, text="Price:", font=('Garamond', 12), bg='white').grid(row=row, column=0, sticky=W, pady=5)
        Entry(manageFrame, textvariable=self.price_var, background='#e9e6d5').grid(row=row, column=1, pady=5)

        row += 1
        Label(manageFrame, text="Quantity:", font=('Garamond', 12), bg='white').grid(row=row, column=0, sticky=W,
                                                                                     pady=5)
        Entry(manageFrame, textvariable=self.quantity_var, background='#e9e6d5').grid(row=row, column=1, pady=5)

        row += 1
        Label(manageFrame, text="Availability:", font=('Garamond', 12), bg='white').grid(row=row, column=0, sticky=W,
                                                                                         pady=5)
        ttk.Combobox(manageFrame, textvariable=self.availability_var, values=["Available", "Out of Stock"], width=13,
                     font=('Garamond', 12), background='#e9e6d5').grid(row=row, column=1, pady=5)

        row += 1
        Label(manageFrame, text="Shelf Life:", font=('Garamond', 12), bg='white').grid(row=row, column=0, sticky=W,
                                                                                       pady=5)
        DateEntry(manageFrame, textvariable=self.shelf_var, date_pattern="yyyy-mm-dd", width=13, font=('Garamond', 12),
                  background='#e9e6d5').grid(row=row, column=1, pady=5)

        row += 1
        Label(manageFrame, text="Supplier:", font=('Garamond', 12), bg='white').grid(row=row, column=0, sticky=W,
                                                                                     pady=5)
        self.supplier_combo = ttk.Combobox(manageFrame, textvariable=self.supplier_var, width=20, font=('Garamond', 12),
                                           state="readonly")
        self.supplier_combo.grid(row=row, column=1, pady=5)

        # Buttons
        btn_row = Frame(manageFrame, bg="white")
        btn_row.grid(row=8, column=0, columnspan=3, pady=20, sticky="ew")

        Button(btn_row, text="Save", width=10, fg='#0a3e34', bg='#e9e6d5', font=('Garamond', 12, 'bold'),
               command=self.save_product).grid(row=0, column=0, padx=5)
        Button(btn_row, text="Update", width=10, fg='#0a3e34', bg='#e9e6d5', font=('Garamond', 12, 'bold'),
               command=self.update_selected).grid(row=0, column=1, padx=5)
        Button(btn_row, text="Delete", width=10, fg='#0a3e34', bg='#e9e6d5', font=('Garamond', 12, 'bold'),
               command=self.archive_selected).grid(row=0, column=2, padx=5)
        Button(btn_row, text="Clear", width=10, fg='#0a3e34', bg='#e9e6d5', font=('Garamond', 12, 'bold'),
               command=self.clear_fields).grid(row=0, column=3, padx=5)

        # Search frame
        searchFrame = LabelFrame(self.prodFrame, text="Search Products", font=('Garamond', 14, 'bold'), padx=10,
                                 pady=10)
        searchFrame.place(x=650, y=90, width=700, height=500)

        Label(searchFrame, text="Search By:", font=('Garamond', 12)).grid(row=0, column=0)
        ttk.Combobox(searchFrame, textvariable=self.search_by_var, values=["PrName", "PrBrand", "Category"],
                     state="readonly").grid(row=0, column=1)
        Entry(searchFrame, textvariable=self.search_var).grid(row=0, column=2)

        # Treeview
        tree_container = Frame(searchFrame)
        tree_container.place(x=0, y=50, width=650, height=400)
        tree_container.grid_propagate(False)
        scroll_y = ttk.Scrollbar(tree_container, orient="vertical")
        scroll_x = ttk.Scrollbar(tree_container, orient="horizontal")
        self.product_tree = ttk.Treeview(tree_container,
                                         columns=("PrID", "PrName", "PrBrand", "Category", "Price", "Quantity",
                                                  "Availability", "ShelfLife"), show="headings",
                                         yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        self.product_tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")
        tree_container.rowconfigure(0, weight=1)
        tree_container.columnconfigure(0, weight=1)
        scroll_y.config(command=self.product_tree.yview)
        scroll_x.config(command=self.product_tree.xview)

        for col in self.product_tree["columns"]:
            self.product_tree.heading(col, text=col)
            self.product_tree.column(col, width=120)

        # Search buttons
        Button(searchFrame, text="Search", width=10, font=('Garamond', 12, 'bold'), fg='#e9e6d5', bg='#0a3e34',
               command=self.search_product).grid(row=0, column=3, padx=5)
        Button(searchFrame, text="Show All", width=10, font=('Garamond', 12, 'bold'), fg='#e9e6d5', bg='#0a3e34',
               command=self.show_all).grid(row=0, column=4, padx=5)
        Button(searchFrame, text="Archive", width=6, font=('Garamond', 12, 'bold'), fg='#e9e6d5', bg='#0a3e34',
               command=self.show_archived).grid(row=0, column=5, padx=5)
        Button(btn_row, text="Revive", width=10, font=('Garamond', 12, 'bold'), fg='#0a3e34', bg='#e9e6d5',
               command=self.revive_selected).grid(row=0, column=4, padx=5)

        self.product_tree.bind("<<TreeviewSelect>>", self.fill_form)

    def clear_fields(self):
        """Clear all fields"""
        self.selected_id.set("")
        self.prname_var.set("")
        self.brand_var.set("")
        self.category_var.set("")
        self.price_var.set("")
        self.quantity_var.set("")
        self.availability_var.set("")
        self.shelf_var.set("")
        self.supplier_var.set("")

    def has_supplier_fk(self):
        """Check if supplier foreign key exists"""
        try:
            db = connect_db()
            cursor = db.cursor()
            cursor.execute(
                """SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=%s AND TABLE_NAME='Product' AND COLUMN_NAME='SupplierID'""",
                ("grocery",))
            result = cursor.fetchone()[0] or 0
            db.close()
            return result > 0
        except:
            return False

    def load_suppliers(self):
        """Load suppliers into combo box"""
        try:
            db = connect_db()
            cur = db.cursor()
            cur.execute("SELECT SupID, Name FROM Supplier WHERE IsArchived=0")
            rows = cur.fetchall()
            options = [f"{r[0]} - {r[1]}" for r in rows]
            self.supplier_combo["values"] = options
            if options:
                self.supplier_combo.set(options[0])
            db.close()
        except:
            self.supplier_combo["values"] = []

    def save_product(self):
        """Save product to database"""
        try:
            name = self.prname_var.get().strip()
            brand = self.brand_var.get().strip()
            category = self.category_var.get().strip()
            price = float(self.price_var.get())
            qty = int(self.quantity_var.get())
            availability = self.availability_var.get().strip()
            shelf = self.shelf_var.get().strip()

            if not name or not brand or not category or not availability or not shelf:
                messagebox.showerror("Error", "Please fill in all required fields")
                return

            supplier_id = None
            if self.supplier_var.get():
                try:
                    supplier_id = int(self.supplier_var.get().split(" - ")[0])
                except:
                    supplier_id = None

            db = connect_db()
            cur = db.cursor()

            if self.has_supplier_fk():
                query = """INSERT INTO Product (PrName, PrBrand, Category, Price, Quantity, Availability, ShelfLife, SupplierID, IsArchived) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,0)"""
                cur.execute(query, (name, brand, category, price, qty, availability, shelf, supplier_id))
            else:
                query = """INSERT INTO Product (PrName, PrBrand, Category, Price, Quantity, Availability, ShelfLife, IsArchived) VALUES (%s,%s,%s,%s,%s,%s,%s,0)"""
                cur.execute(query, (name, brand, category, price, qty, availability, shelf))

            db.commit()
            db.close()

            self.show_all()
            self.clear_fields()
            messagebox.showinfo("Success", "Product added successfully.")
        except ValueError:
            messagebox.showerror("Error", "Price must be a number and Quantity an integer")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))

    def update_selected(self):
        """Update selected product"""
        if not self.selected_id.get():
            messagebox.showwarning("Select", "Select a product to update.")
            return

        try:
            name = self.prname_var.get().strip()
            brand = self.brand_var.get().strip()
            category = self.category_var.get().strip()
            price = float(self.price_var.get())
            qty = int(self.quantity_var.get())
            availability = self.availability_var.get().strip()
            shelf = self.shelf_var.get().strip()

            supplier_id = None
            if self.supplier_var.get():
                try:
                    supplier_id = int(self.supplier_var.get().split(" - ")[0])
                except:
                    supplier_id = None

            db = connect_db()
            cur = db.cursor()

            if self.has_supplier_fk():
                query = """UPDATE Product SET PrName=%s, PrBrand=%s, Category=%s, Price=%s, Quantity=%s, Availability=%s, ShelfLife=%s, SupplierID=%s WHERE PrID=%s"""
                cur.execute(query, (name, brand, category, price, qty, availability, shelf, supplier_id,
                                    self.selected_id.get()))
            else:
                query = """UPDATE Product SET PrName=%s, PrBrand=%s, Category=%s, Price=%s, Quantity=%s, Availability=%s, ShelfLife=%s WHERE PrID=%s"""
                cur.execute(query, (name, brand, category, price, qty, availability, shelf, self.selected_id.get()))

            db.commit()
            db.close()

            self.show_all()
            self.clear_fields()
            messagebox.showinfo("Updated", "Product updated.")
        except ValueError:
            messagebox.showerror("Error", "Price must be a number and Quantity an integer")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))

    def archive_selected(self):
        """Archive selected product"""
        if not self.selected_id.get():
            messagebox.showwarning("Select", "Select a product to archive.")
            return

        db = connect_db()
        cur = db.cursor()
        cur.execute("UPDATE Product SET IsArchived=1 WHERE PrID=%s", (self.selected_id.get(),))
        db.commit()
        db.close()

        self.show_all()
        self.clear_fields()
        messagebox.showinfo("Archived", "Product archived successfully.")

    def revive_selected(self):
        """Revive archived product"""
        if not self.selected_id.get():
            messagebox.showwarning("Select", "Select a product to revive.")
            return

        db = connect_db()
        cur = db.cursor()
        cur.execute("UPDATE Product SET IsArchived=0 WHERE PrID=%s", (self.selected_id.get(),))
        db.commit()
        db.close()

        self.show_archived()
        self.clear_fields()
        messagebox.showinfo("Restored", "Product restored successfully.")

    def search_product(self):
        """Search products"""
        keyword = self.search_var.get()
        field = self.search_by_var.get()

        if field == "":
            messagebox.showwarning("Warning", "Select a field to search.")
            return

        db = connect_db()
        cur = db.cursor()

        if self.has_supplier_fk():
            query = f"""SELECT p.PrID, p.PrName, p.PrBrand, p.Category, p.Price, p.Quantity, p.Availability, p.ShelfLife, COALESCE(s.Name, '') AS Supplier FROM Product p LEFT JOIN Supplier s ON p.SupplierID = s.SupID WHERE p.{field} LIKE %s AND p.IsArchived = 0"""
        else:
            query = f"""SELECT p.PrID, p.PrName, p.PrBrand, p.Category, p.Price, p.Quantity, p.Availability, p.ShelfLife, '' AS Supplier FROM Product p WHERE p.{field} LIKE %s AND p.IsArchived = 0"""

        cur.execute(query, (f"%{keyword}%",))
        rows = cur.fetchall()
        db.close()

        self.product_tree.delete(*self.product_tree.get_children())
        for row in rows:
            self.product_tree.insert("", END, values=row)

    def show_all(self):
        """Show all products"""
        db = connect_db()
        cur = db.cursor()

        if self.has_supplier_fk():
            cur.execute(
                """SELECT p.PrID, p.PrName, p.PrBrand, p.Category, p.Price, p.Quantity, p.Availability, p.ShelfLife, COALESCE(s.Name, '') AS Supplier FROM Product p LEFT JOIN Supplier s ON p.SupplierID = s.SupID WHERE p.IsArchived=0""")
        else:
            cur.execute(
                """SELECT p.PrID, p.PrName, p.PrBrand, p.Category, p.Price, p.Quantity, p.Availability, p.ShelfLife, '' AS Supplier FROM Product p WHERE p.IsArchived=0""")

        rows = cur.fetchall()
        db.close()

        self.product_tree.delete(*self.product_tree.get_children())
        for r in rows:
            self.product_tree.insert("", END, values=r)

    def show_archived(self):
        """Show archived products"""
        db = connect_db()
        cur = db.cursor()

        if self.has_supplier_fk():
            cur.execute(
                """SELECT p.PrID, p.PrName, p.PrBrand, p.Category, p.Price, p.Quantity, p.Availability, p.ShelfLife, COALESCE(s.Name, '') AS Supplier FROM Product p LEFT JOIN Supplier s ON p.SupplierID = s.SupID WHERE p.IsArchived=1""")
        else:
            cur.execute(
                """SELECT p.PrID, p.PrName, p.PrBrand, p.Category, p.Price, p.Quantity, p.Availability, p.ShelfLife, '' AS Supplier FROM Product p WHERE p.IsArchived=1""")

        rows = cur.fetchall()
        db.close()

        self.product_tree.delete(*self.product_tree.get_children())
        for r in rows:
            self.product_tree.insert("", END, values=r)

    def fill_form(self, event):
        """Fill form from selected product"""
        values = self.product_tree.item(self.product_tree.focus(), "values")
        if values:
            self.selected_id.set(values[0])
            self.prname_var.set(values[1])
            self.brand_var.set(values[2])
            self.category_var.set(values[3])
            self.price_var.set(values[4])
            self.quantity_var.set(values[5])
            self.availability_var.set(values[6])
            self.shelf_var.set(values[7])

            try:
                if self.has_supplier_fk():
                    db = connect_db()
                    cur = db.cursor()
                    cur.execute(
                        """SELECT s.SupID, s.Name FROM Supplier s JOIN Product p ON p.SupplierID = s.SupID WHERE p.PrID=%s""",
                        (values[0],))
                    res = cur.fetchone()
                    if res:
                        self.supplier_var.set(f"{res[0]} - {res[1]}")
                    else:
                        self.supplier_var.set("")
                    db.close()
            except:
                self.supplier_var.set("")

    def close_form(self):
        """Close product form"""
        self.prodFrame.place_forget()


# ================= SALES FORM CLASS =================
class SalesForm:
    def __init__(self, parent_window):
        self.parent = parent_window

        # Create sales frame
        self.saleFrame = Frame(parent_window, width=1400, height=608, bg="#e9e6d5")
        self.saleFrame.place(x=200, y=150)

        header = Label(self.saleFrame, text="Sales & Receipts Viewer", font=('Garamond', 16, 'bold'), bg="#e9e6d5",
                       fg="#0a3e34")
        header.place(x=0, y=0, relwidth=1, height=40)

        back_btn = Button(self.saleFrame, text="Back", font=('Garamond', 10, 'bold'), cursor='hand2',
                          command=self.close_form, bg="#e9e6d5", fg="#0a3e34")
        back_btn.place(x=10, y=50)

        self.period_var = StringVar(value="all")
        self.create_sales_ui()
        self.load_receipts("all")

    def create_sales_ui(self):
        """Create sales interface"""
        # Filter frame
        filter_frame = Frame(self.saleFrame, bg="#e9e6d5")
        filter_frame.place(x=100, y=45, width=900, height=40)

        total_label = Label(self.saleFrame, text="Total: ₱0.00", font=('Garamond', 14, 'bold'), bg="#e9e6d5",
                            fg="#0a3e34")
        total_label.place(x=1050, y=50)

        # Period buttons
        btn_all = Button(filter_frame, text="All", font=('Garamond', 12, 'bold'), bg="#0a3e34", fg="white",
                         command=lambda: self.set_period("all"), width=10)
        btn_daily = Button(filter_frame, text="Daily", font=('Garamond', 12, 'bold'), bg="#0a3e34", fg="white",
                           command=lambda: self.set_period("daily"), width=10)
        btn_weekly = Button(filter_frame, text="Weekly", font=('Garamond', 12, 'bold'), bg="#0a3e34", fg="white",
                            command=lambda: self.set_period("weekly"), width=10)
        btn_monthly = Button(filter_frame, text="Monthly", font=('Garamond', 12, 'bold'), bg="#0a3e34", fg="white",
                             command=lambda: self.set_period("monthly"), width=10)
        btn_yearly = Button(filter_frame, text="Yearly", font=('Garamond', 12, 'bold'), bg="#0a3e34", fg="white",
                            command=lambda: self.set_period("yearly"), width=10)

        btn_all.pack(side=LEFT, padx=5)
        btn_daily.pack(side=LEFT, padx=5)
        btn_weekly.pack(side=LEFT, padx=5)
        btn_monthly.pack(side=LEFT, padx=5)
        btn_yearly.pack(side=LEFT, padx=5)

        # List frame
        list_frame = Frame(self.saleFrame, bg="white", bd=2, relief=RIDGE)
        list_frame.place(x=10, y=100, width=900, height=480)

        scrolly = ttk.Scrollbar(list_frame, orient="vertical")
        scrollx = ttk.Scrollbar(list_frame, orient="horizontal")

        self.tree = ttk.Treeview(list_frame, columns=("bill", "date", "time", "cashier", "customer", "total"),
                                 show="headings", yscrollcommand=scrolly.set, xscrollcommand=scrollx.set)
        self.tree.pack(fill=BOTH, expand=True)

        scrolly.config(command=self.tree.yview)
        scrollx.config(command=self.tree.xview)

        self.tree.heading("bill", text="Bill No")
        self.tree.heading("date", text="Date")
        self.tree.heading("time", text="Time")
        self.tree.heading("cashier", text="Cashier")
        self.tree.heading("customer", text="Customer")
        self.tree.heading("total", text="Total")

        self.tree.column("bill", width=80)
        self.tree.column("date", width=100)
        self.tree.column("time", width=80)
        self.tree.column("cashier", width=140)
        self.tree.column("customer", width=140)
        self.tree.column("total", width=100)

        # Detail frame
        detail_frame = Frame(self.saleFrame, bg="white", bd=2, relief=RIDGE)
        detail_frame.place(x=930, y=100, width=450, height=480)

        self.receipt_text = Text(detail_frame, font=("courier new", 10))
        self.receipt_text.pack(fill=BOTH, expand=True)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.total_label = total_label

    def parse_receipt(self, path):
        """Parse receipt file"""
        try:
            with open(path, "r") as f:
                content = f.read()
            bill = None
            m = re.search(r"Bill No\s*:\s*(\d+)", content)
            if m:
                bill = m.group(1)
            dt = None
            tm = None
            m = re.search(r"Date\s*:\s*([0-9]{2}/[0-9]{2}/[0-9]{4}).*?Time:\s*([0-9]{2}:[0-9]{2}:[0-9]{2})", content,
                          re.S)
            if m:
                dt = m.group(1)
                tm = m.group(2)
            cashier = ""
            m = re.search(r"Cashier\s*:\s*(.+)", content)
            if m:
                cashier = m.group(1).strip()
            customer = ""
            m = re.search(r"Customer\s*:\s*(.+)", content)
            if m:
                customer = m.group(1).strip()
            total = 0.0
            m = re.search(r"Total Amount:[^\n]*PHP\s*([0-9]+(?:\.[0-9]+)?)", content)
            if m:
                try:
                    total = float(m.group(1))
                except:
                    total = 0.0
            parsed_date = None
            if dt:
                try:
                    parsed_date = datetime.strptime(dt, "%d/%m/%Y").date()
                except:
                    parsed_date = None
            return {"bill": bill or os.path.basename(path).replace(".txt", ""), "date": dt or "", "time": tm or "",
                    "cashier": cashier, "customer": customer, "total": total, "path": path, "parsed_date": parsed_date}
        except:
            return None

    def load_receipts(self, period):
        """Load receipts based on period"""
        self.tree.delete(*self.tree.get_children())
        total_sum = 0.0
        today = date.today()
        start = None
        end = None

        if period == "daily":
            start = today
            end = today
        elif period == "weekly":
            start = today - timedelta(days=6)
            end = today
        elif period == "monthly":
            start = today.replace(day=1)
            end = today
        elif period == "yearly":
            start = date(today.year, 1, 1)
            end = today

        receipts = []
        if os.path.isdir("bills"):
            for fname in os.listdir("bills"):
                if fname.endswith(".txt"):
                    info = self.parse_receipt(os.path.join("bills", fname))
                    if info:
                        d = info["parsed_date"]
                        if start and end:
                            if not d or d < start or d > end:
                                continue
                        receipts.append(info)

        receipts.sort(key=lambda r: (r["parsed_date"] or date(1970, 1, 1), r["time"]))
        for r in receipts:
            total_sum += r["total"]
            self.tree.insert("", END, values=(r["bill"], r["date"], r["time"], r["cashier"], r["customer"],
                                              f"₱{r['total']:,.2f}"))

        self.total_label.config(text=f"Total: ₱{total_sum:,.2f}")

    def on_select(self, ev):
        """Handle tree selection"""
        f = self.tree.focus()
        vals = self.tree.item(f, "values")
        if not vals:
            return
        bill = vals[0]
        path = None
        bp = os.path.join("bills", f"{bill}.txt")
        if os.path.exists(bp):
            path = bp
        else:
            for fname in os.listdir("bills"):
                if fname.endswith(".txt") and fname.startswith(str(bill)):
                    path = os.path.join("bills", fname)
                    break

        self.receipt_text.delete("1.0", END)
        if path and os.path.exists(path):
            with open(path, "r") as f:
                self.receipt_text.insert(END, f.read())

    def set_period(self, period):
        """Set period filter"""
        self.period_var.set(period)
        self.load_receipts(period)

    def close_form(self):
        """Close sales form"""
        self.saleFrame.place_forget()


# ================= MAIN APPLICATION =================
class GroceryManagementSystem:
    def __init__(self):
        # Create main login window
        self.root = Tk()
        self.login_app = LoginClass(self.root)
        self.root.mainloop()


# ================= ENTRY POINT =================
if __name__ == "__main__":

    app = GroceryManagementSystem()
