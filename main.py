import datetime
import pandas as pd

class ExpenseTracker:
    def __init__(self):
        self.entries = {}

    def add_entry(self, mode, description, date=None):
        if date is None:
            date = datetime.datetime.now()
        month_year = date.strftime('%Y-%m')
        if month_year not in self.entries:
            self.entries[month_year] = []
        self.entries[month_year].append({
            'mode': mode,
            'description': description,
            'date': date
        })

    def view_entries(self, month, year):
        month_year = f'{year}-{month:02d}'
        if month_year in self.entries:
            entries = self.entries[month_year]
            for index, entry in enumerate(entries, start=1):
                print(f"{index}. Date: {entry['date']}, Mode: {entry['mode']}, Description: {entry['description']}")
        else:
            print("No entries for the selected month and year.")

    def edit_entry(self, month, year, entry_index, new_mode, new_description):
        month_year = f'{year}-{month:02d}'
        if month_year in self.entries:
            entries = self.entries[month_year]
            if 0 < entry_index <= len(entries):
                entries[entry_index - 1]['mode'] = new_mode
                entries[entry_index - 1]['description'] = new_description
                print("Entry edited successfully.")
            else:
                print("Invalid entry index.")
        else:
            print("No entries for the selected month and year.")

    def delete_entry(self, month, year, entry_index):
        month_year = f'{year}-{month:02d}'
        if month_year in self.entries:
            entries = self.entries[month_year]
            if 0 < entry_index <= len(entries):
                deleted_entry = entries.pop(entry_index - 1)
                print("Entry deleted successfully.")
            else:
                print("Invalid entry index.")
        else:
            print("No entries for the selected month and year.")

    def export_to_excel(self, month, year):
        month_year = f'{year}-{month:02d}'
        if month_year in self.entries:
            entries = self.entries[month_year]
            df = pd.DataFrame(entries)
            file_name = f'Expense_Tracker_{year}-{month:02d}.xlsx'
            df.to_excel(file_name, index=False)
            print(f"Data exported to {file_name}.")
        else:
            print("No entries for the selected month and year.")

def main():
    tracker = ExpenseTracker()

    while True:
        print("Main Menu")
        print("1. New Entry")
        print("2. View Entries")
        print("3. Edit Entry")
        print("4. Delete Entry")
        print("5. Export to Excel")
        print("6. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            mode = input("Enter mode of transaction: ")
            description = input("Enter description: ")
            tracker.add_entry(mode, description)

        elif choice == '2':
            year = int(input("Enter year: "))
            month = int(input("Enter month: "))
            tracker.view_entries(month, year)

        elif choice == '3':
            year = int(input("Enter year: "))
            month = int(input("Enter month: "))
            tracker.view_entries(month, year)
            entry_index = int(input("Enter the index of the entry to edit: "))
            new_mode = input("Enter new mode of transaction: ")
            new_description = input("Enter new description: ")
            tracker.edit_entry(month, year, entry_index, new_mode, new_description)

        elif choice == '4':
            year = int(input("Enter year: "))
            month = int(input("Enter month: "))
            tracker.view_entries(month, year)
            entry_index = int(input("Enter the index of the entry to delete: "))
            tracker.delete_entry(month, year, entry_index)

        elif choice == '5':
            year = int(input("Enter year: "))
            month = int(input("Enter month: "))
            tracker.export_to_excel(month, year)

        elif choice == '6':
            print("Exiting the program.")
            break

        else:
            print("Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    main()
