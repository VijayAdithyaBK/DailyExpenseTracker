import tkinter as tk
from tkinter import messagebox, ttk
import datetime
from tkcalendar import Calendar
import pickle
from tkinter.simpledialog import askstring
import pandas as pd
from ttkthemes import ThemedStyle


class ExpenseTrackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Daily Expense Tracker")
        self.root.geometry("400x300")

        # Apply the "Plastik" theme
        self.style = ThemedStyle(self.root)
        self.style.set_theme("plastik")

        self.tracker = ExpenseTracker()

        self.load_data()  # Load saved data

        self.create_main_screen()

    def load_data(self):
        try:
            with open('data.pkl', 'rb') as file:
                saved_data = pickle.load(file)
                self.tracker.modes = saved_data.get('modes', [])
                self.tracker.entries = saved_data.get('entries', {})
        except FileNotFoundError:
            pass

    def save_data(self):
        data = {
            'modes': self.tracker.modes,
            'entries': self.tracker.entries,
        }
        with open('data.pkl', 'wb') as file:
            pickle.dump(data, file)

    def create_main_screen(self):
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        self.add_entry_button = tk.Button(self.root, text="Add New Entry", command=self.open_add_entry_window)
        self.add_entry_button.pack(pady=10)

        self.view_entries_button = tk.Button(self.root, text="View Entries", command=self.open_view_entries_window)
        self.view_entries_button.pack()

        self.settings_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.settings_menu.add_command(label="Edit Modes", command=self.edit_modes)
        self.settings_menu.add_command(label="Delete Modes", command=self.delete_modes)
        self.menu_bar.add_cascade(label="Settings", menu=self.settings_menu)

    def open_add_entry_window(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Add New Entry")
        add_window.geometry("400x300")  # Set the fixed dimensions

        self.mode_label = tk.Label(add_window, text="Mode of Transaction:")
        self.mode_label.pack()

        self.mode_var = tk.StringVar()
        self.mode_combobox = ttk.Combobox(add_window, textvariable=self.mode_var)
        self.mode_combobox['values'] = self.tracker.get_modes()
        self.mode_combobox.pack()

        self.amount_label = tk.Label(add_window, text="Amount:")
        self.amount_label.pack()

        self.amount_entry = tk.Entry(add_window)
        self.amount_entry.pack()

        self.desc_label = tk.Label(add_window, text="Description:")
        self.desc_label.pack()

        self.desc_entry = tk.Entry(add_window)
        self.desc_entry.pack()

        self.date_label = tk.Label(add_window, text="Date:")
        self.date_label.pack()

        self.date_picker = Calendar(add_window, selectmode='day')
        self.date_picker.pack()

        self.save_button = tk.Button(add_window, text="Save", command=self.save_entry)
        self.save_button.pack()

        self.discard_button = tk.Button(add_window, text="Discard", command=add_window.destroy)
        self.discard_button.pack()

    def open_view_entries_window(self):
        view_window = tk.Toplevel(self.root)
        view_window.title("View Entries")
        view_window.geometry("400x300")  # Set the fixed dimensions

        year_label = tk.Label(view_window, text="Year:")
        year_label.pack()

        self.year_entry = tk.Entry(view_window)
        self.year_entry.pack()

        month_label = tk.Label(view_window, text="Month (1-12):")
        month_label.pack()

        self.month_entry = tk.Entry(view_window)
        self.month_entry.pack()

        self.view_button = tk.Button(view_window, text="View", command=self.display_entries)
        self.view_button.pack()

    def display_entries(self):
        year = int(self.year_entry.get())
        month = int(self.month_entry.get())

        entries = self.tracker.get_entries(year, month)

        if entries:
            entries_window = tk.Toplevel(self.root)
            entries_window.title(f"Entries for {month}/{year}")

            tree = ttk.Treeview(entries_window, columns=("Date", "Mode", "Amount", "Description"))
            tree.heading("Date", text="Date")
            tree.heading("Mode", text="Mode")
            tree.heading("Amount", text="Amount")
            tree.heading("Description", text="Description")

            for entry in entries:
                tree.insert("", "end", values=(entry['date'], entry['mode'], entry['amount'], entry['description']))

            tree.pack()

            delete_button = tk.Button(entries_window, text="Delete Entries",
                                      command=lambda: self.delete_selected_entries(tree))
            export_button = tk.Button(entries_window, text="Export to Excel",
                                      command=lambda: self.export_to_excel(entries))

            delete_button.pack(side="left")
            export_button.pack(side="left")

    def toggle_edit_mode(self, tree):
        for child in tree.get_children():
            for col in range(4):
                entry = tree.item(child, "values")[col]
                cell = tree.set(child, col)
                if entry != cell:
                    tree.set(child, col, entry)
                else:
                    tree.tag_configure("editable", background="light blue")
                    tree.item(child, tags=("editable",))

    def toggle_delete_mode(self, tree):
        for child in tree.get_children():
            tree.tag_bind(child, "<Button-1>", lambda event, tree=tree: self.toggle_checkbox(event, tree))
            tree.insert(child, "end", values=["", "", "", ""], tags="checkbox")

    def toggle_checkbox(self, event, tree):
        item = tree.identify_row(event.y)
        if tree.tag_has(item, "checkbox"):
            if tree.tag_has(item, "selected"):
                tree.tag_remove("selected", item)
            else:
                tree.tag_add("selected", item)

    def delete_selected_entries(self, tree):
        selected_items = tree.selection()
        entries_to_delete = []

        for item in selected_items:
            values = tree.item(item, "values")
            entry = {
                'date': values[0],
                'mode': values[1],
                'amount': values[2],
                'description': values[3]
            }
            entries_to_delete.append(entry)

        for entry in entries_to_delete:
            self.tracker.remove_entry(entry)
            tree.delete(tree.selection())

        self.save_data()
        messagebox.showinfo("Success", "Selected entries deleted successfully!")

    def export_to_excel(self, entries):
        if not entries:
            messagebox.showinfo("Info", "No entries to export.")
            return

        data = {
            "Date": [entry['date'] for entry in entries],
            "Mode": [entry['mode'] for entry in entries],
            "Amount": [entry['amount'] for entry in entries],
            "Description": [entry['description'] for entry in entries],
        }

        df = pd.DataFrame(data)
        df.to_excel("expense_entries.xlsx", index=False)
        messagebox.showinfo("Info", "Entries exported to 'expense_entries.xlsx'")

    def save_entry(self):
        mode = self.mode_var.get()
        amount = self.amount_entry.get()
        description = self.desc_entry.get()
        date_str = self.date_picker.get_date()  # Get date as string

        if mode and amount and description and date_str:
            # Convert string date to datetime.date using the correct format
            date = datetime.datetime.strptime(date_str, "%m/%d/%y").date()
            datetime_obj = datetime.datetime.combine(date, datetime.time.min)  # Set time to midnight

            self.tracker.add_entry(mode, description, amount, datetime_obj)
            self.save_data()
            messagebox.showinfo("Success", "Entry added successfully!")
            self.root.update_idletasks()
            self.root.update()
            self.discard_button.invoke()
        else:
            messagebox.showerror("Error", "All fields are required!")

    def increment_hour(self):
        self.hour.set((self.hour.get() + 1) % 12)

    def decrement_hour(self):
        self.hour.set((self.hour.get() - 1) % 12)

    def increment_minute(self):
        self.minute.set((self.minute.get() + 1) % 60)

    def decrement_minute(self):
        self.minute.set((self.minute.get() - 1) % 60)

    def add_new_mode(self):
        new_mode = askstring("Add New Mode", "Enter new mode of transaction:")
        if new_mode:
            self.tracker.add_mode(new_mode)
            self.edit_combobox['values'] = self.tracker.get_modes()  # Update the edit_combobox
            self.edit_var.set(new_mode)  # Update the edit_var

    def edit_modes(self):
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Modes")
        edit_window.geometry("300x200")  # Set the fixed dimensions

        self.edit_label = tk.Label(edit_window, text="Edit Transaction Modes:")
        self.edit_label.pack()

        self.edit_var = tk.StringVar()
        self.edit_combobox = ttk.Combobox(edit_window, textvariable=self.edit_var, values=self.tracker.get_modes())
        self.edit_combobox.pack()

        self.edit_entry = tk.Entry(edit_window)
        self.edit_entry.pack()

        self.edit_button = tk.Button(edit_window, text="Edit", command=self.update_mode)
        self.edit_button.pack()

        self.add_mode_button = tk.Button(edit_window, text="Add New Mode", command=self.add_new_mode)
        self.add_mode_button.pack()  # Add the button to the edit_window

    def update_mode(self):
        selected_mode = self.edit_var.get()
        updated_mode = self.edit_entry.get()

        if selected_mode and updated_mode:
            self.tracker.update_mode(selected_mode, updated_mode)
            self.edit_combobox['values'] = self.tracker.get_modes()
            self.edit_var.set(updated_mode)
            self.edit_entry.delete(0, tk.END)
            messagebox.showinfo("Success", "Mode updated successfully!")
        else:
            messagebox.showerror("Error", "Please select a mode and enter an update!")

    def delete_modes(self):
        delete_window = tk.Toplevel(self.root)
        delete_window.title("Delete Modes")
        delete_window.geometry("300x200")  # Set the fixed dimensions

        self.delete_label = tk.Label(delete_window, text="Delete Transaction Modes:")
        self.delete_label.pack()

        self.delete_var = tk.StringVar()
        self.delete_combobox = ttk.Combobox(delete_window, textvariable=self.delete_var, values=self.tracker.get_modes())
        self.delete_combobox.pack()

        self.delete_button = tk.Button(delete_window, text="Delete", command=self.remove_mode)
        self.delete_button.pack()

    def remove_mode(self):
        mode_to_remove = self.delete_var.get()

        if mode_to_remove:
            self.tracker.remove_mode(mode_to_remove)
            self.delete_combobox['values'] = self.tracker.get_modes()
            self.delete_var.set("")
            messagebox.showinfo("Success", "Mode deleted successfully!")
        else:
            messagebox.showerror("Error", "Please select a mode to delete!")

    def save_and_exit(self):
        self.save_data()  # Save data before exiting
        self.root.destroy()

class ExpenseTracker:
    def __init__(self):
        self.entries = {}
        self.modes = ["Cash", "Credit Card", "Debit Card"]  # Default modes

    def add_mode(self, mode):
        if mode not in self.modes:
            self.modes.append(mode)

    def update_mode(self, selected_mode, updated_mode):
        if selected_mode in self.modes:
            index = self.modes.index(selected_mode)
            self.modes[index] = updated_mode

    def remove_mode(self, mode):
        if mode in self.modes:
            self.modes.remove(mode)

    def get_modes(self):
        return self.modes

    def add_entry(self, mode, description, amount, date):
        self.entries.setdefault(date.year, {}).setdefault(date.month, []).append({
            'mode': mode,
            'description': description,
            'amount': amount,
            'date': date.strftime('%Y-%m-%d')
        })

    def remove_entry(self, entry):
        year = int(entry['date'].split('-')[0])
        month = int(entry['date'].split('-')[1])
        self.entries[year][month].remove(entry)

        if not self.entries[year][month]:
            del self.entries[year][month]
            if not self.entries[year]:
                del self.entries[year]

    def get_entries(self, year, month):
        return self.entries.get(year, {}).get(month, [])

def main():
    root = tk.Tk()
    app = ExpenseTrackerGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.save_and_exit)  # Save data on exit
    root.mainloop()

if __name__ == "__main__":
    main()