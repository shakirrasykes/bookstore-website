import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import os
import threading
from tkinter import simpledialog
from PIL import Image, ImageTk  # For handling images

print(f"Attempting to connect to database at: {os.path.abspath('bookstore (1) (1).db')}")

# Function to connect to the database using a context manager (with statement)
def connect_db():
    return sqlite3.connect('bookstore (1) (1).db', check_same_thread=False)  # Set check_same_thread to False for threading

# Create tables if they do not exist
def create_tables():
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS Books (
        id INTEGER PRIMARY KEY, author_first_name TEXT, author_last_name TEXT, 
        book_title TEXT, genre TEXT, publication_date TEXT, price REAL, 
        isbn TEXT, city_tax_denver REAL, state_tax_co REAL, total_price_incl_tax REAL, image TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Customer_Orders (
        order_id INTEGER PRIMARY KEY, customer_id INTEGER, book_title TEXT, quantity_sold INTEGER, order_status TEXT, order_date TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Customers (
        customer_id INTEGER PRIMARY KEY, name TEXT, email TEXT, phone TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Manufacturer_Orders (
        order_id INTEGER PRIMARY KEY, book_id INTEGER, order_quantity INTEGER, order_date TEXT, status TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Sales (
        sale_id INTEGER PRIMARY KEY, book_id TEXT, quantity_sold INTEGER, quantity_on_hand INTEGER, remaining_quantity INTEGER, total_price INTEGER, sale_date TEXT, 
        tracking_number TEXT, order_id INTEGER, customer_name TEXT, payment_method TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY, name TEXT, email TEXT, password TEXT, created_at TEXT)''')

    conn.commit()
    conn.close()

# Fetch data for a specific table
def get_data(table, filter_column=None, filter_value=None):
    conn = connect_db()
    cursor = conn.cursor()
    
    if filter_column and filter_value:  # Apply filtering if values are provided
        cursor.execute(f"SELECT * FROM {table} WHERE {filter_column} LIKE ?", ('%' + filter_value + '%',))
    else:
        cursor.execute(f"SELECT * FROM {table}")  # Fetch all data if no filter
    rows = cursor.fetchall()
    conn.close()
    return rows

# Refresh treeview display
def refresh_treeview(tree, table, filter_column=None, filter_value=None):
    # Clear current rows
    for row in tree.get_children():
        tree.delete(row)

    # Get data, applying the filter if present
    rows = get_data(table, filter_column, filter_value)

    # Insert the filtered rows into the treeview
    for record in rows:
        if table == "Sales":  # Special handling for the Sales table
            # Round the total_price value (assumed to be at index 5)
            record = list(record)
            record[5] = round(record[5], 2)  # Round to 2 decimal places
            record = tuple(record)
        tree.insert('', 'end', values=record)

# Function to add an entry into a table
def add_entry(table, fields):
    try:
        conn = connect_db()
        cursor = conn.cursor()

        columns = ', '.join(fields.keys())
        placeholders = ', '.join(['?'] * len(fields))
        values = tuple(fields.values())

        cursor.execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", values)

        conn.commit()

        # After the insert, check if remaining_quantity <= 1 for Sales table
        if table == "Sales":  # Ensure we're checking the correct table
            cursor.execute("SELECT remaining_quantity, book_id FROM Sales WHERE sale_id = ?", (cursor.lastrowid,))
            result = cursor.fetchone()
            if result:
                remaining_quantity, book_id = result

                if remaining_quantity <= 1:
                    messagebox.showwarning("Low Stock Alert", "Remaining stock for this item is at or below 1. Placing an order for 10 more items.")

                    # Add an order to the Manufacturer_Orders table
                    order_quantity = 10  # Set the order quantity to 10
                    order_date = "2023-10-01"  # Set a default order date (you can modify this logic)
                    status = "Pending"  # Set the initial status

                    # Insert the order into the Manufacturer_Orders table
                    cursor.execute('''INSERT INTO Manufacturer_Orders (book_id, order_quantity, order_date, status)
                                     VALUES (?, ?, ?, ?)''', (book_id, order_quantity, order_date, status))
                    conn.commit()

                    # Refresh the Manufacturer_Orders treeview
                    refresh_treeview(trees['Manufacturer_Orders'], 'Manufacturer_Orders')

        conn.close()
        refresh_treeview(trees[table], table)
        messagebox.showinfo("Success", f"Entry added to {table} successfully!")
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add entry to {table}: {e}")

# Wrapper to run the add_entry function in a separate thread
def add_entry_threaded(table, fields):
    def insert_entry():
        add_entry(table, fields)
        # After the entry is added, refresh the treeview
        root.after(0, lambda: refresh_treeview(trees[table], table))

    threading.Thread(target=insert_entry).start()

def delete_entry(table, selection=None):
    try:
        # If selection is None (manual ID entry), prompt user to input the ID
        if not selection:
            item_id = simpledialog.askinteger(f"Delete {table[:-1]}", f"Enter the ID of the {table[:-1]} to delete:")

            if item_id is None:  # If user cancels input
                return

            # Confirm deletion
            confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete {table[:-1]} with ID {item_id}?")
            if not confirm:
                return

            # Proceed with deletion
            perform_deletion(table, item_id)

        else:
            item_id = trees[table].item(selection)['values'][0]  # The ID is in the first column
            perform_deletion(table, item_id)

        # Refresh the treeview after the deletion
        refresh_treeview(trees[table], table)
        messagebox.showinfo("Success", f"{table[:-1]} with ID {item_id} deleted successfully!")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to delete entry from {table}: {e}")

def perform_deletion(table, item_id):
    # Dynamically determine the primary key column for each table
    primary_key_column = 'id'  # Default primary key column
    if table == 'Books':
        primary_key_column = 'id'
    elif table == 'Customer_Orders':
        primary_key_column = 'order_id'
    elif table == 'Customers':
        primary_key_column = 'customer_id'
    elif table == 'Manufacturer_Orders':
        primary_key_column = 'order_id'
    elif table == 'Sales':
        primary_key_column = 'sale_id'
    elif table == 'Users':
        primary_key_column = 'user_id'

    # Connect to the database and execute the delete query
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(f"DELETE FROM {table} WHERE {primary_key_column} = ?", (item_id,))
        conn.commit()

        # Reset the auto-incrementing order_id for Manufacturer_Orders table
        if table == 'Manufacturer_Orders':
            cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'Manufacturer_Orders'")
            conn.commit()

    except Exception as e:
        print(f"Error deleting entry: {e}")
    finally:
        conn.close()

# Function to update an entry in the table using the ID
def update_entry(table, tree):
    try:
        # Get the selected row from the Treeview
        selected_item = tree.selection()

        if not selected_item:
            messagebox.showerror("Error", f"No {table[:-1]} selected!")
            return

        # Get the ID of the selected item (assuming the ID is in the first column)
        item_id = tree.item(selected_item)['values'][0]  # Adjust if ID is in a different column

        # Get the updated data from the input fields
        updated_fields = {column: entries[table][column].get() for column in tables[table]}

        # Prepare the update query
        columns = ', '.join([f"{key} = ?" for key in updated_fields.keys() if updated_fields[key] != ""])  # Exclude empty fields
        values = tuple(value for value in updated_fields.values() if value != "") + (item_id,)

        if not columns:  # If no fields are updated, show error
            messagebox.showerror("Error", "No valid fields to update.")
            return

        # Execute the update query
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(f"UPDATE {table} SET {columns} WHERE id = ?", values)
        conn.commit()
        conn.close()

        # Refresh the Treeview to reflect the changes
        refresh_treeview(tree, table)
        messagebox.showinfo("Success", f"{table[:-1]} with ID {item_id} updated successfully!")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to update entry in {table}: {e}")

# Function to display an image
def display_image(image_path, image_label):
    try:
        if image_path and os.path.exists(image_path):  # Check if the path exists
            print(f"Loading image from: {image_path}")  # Debugging: Print the image path
            img = Image.open(image_path)
            img = img.resize((100, 150), Image.ANTIALIAS)  # Resize the image
            img_tk = ImageTk.PhotoImage(img)
            image_label.config(image=img_tk)
            image_label.image = img_tk  # Keep a reference to avoid garbage collection
        else:
            print(f"Image path does not exist or is invalid: {image_path}")  # Debugging: Print if the path is invalid
            image_label.config(image=None)  # Clear the label if no image is found
    except Exception as e:
        print(f"Error loading image: {e}")  # Debugging: Print any errors
        image_label.config(image=None)

# Function to handle row selection and populate input fields
def on_treeview_select(event, tree, table, image_label):
    selected_item = tree.selection()

    if not selected_item:
        return  # No selection made

    # Get the selected item’s ID (assuming ID is the first column)
    item_id = tree.item(selected_item)['values'][0]

    # Fetch the data for the selected row
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table} WHERE id = ?", (item_id,))
    current_data = cursor.fetchone()
    conn.close()

    if not current_data:
        messagebox.showerror("Error", "Failed to fetch data for the selected item.")
        return

    # Populate the input fields with the selected row data
    for i, column in enumerate(tables[table]):
        entries[table][column].delete(0, tk.END)  # Clear the existing input
        entries[table][column].insert(0, current_data[i])  # Populate with selected row data

    # Display the image if the selected row has an image path
    if table == "Books":  # Only for the Books table
        image_path = current_data[-1]  # Assuming 'image' is the last column
        print(f"Selected image path: {image_path}")  # Debugging: Print the selected image path
        display_image(image_path, image_label)

# Function to apply filter
def apply_filter(tree, table, filter_value_entry, filter_column_var):
    print("Apply Filter Button Clicked!")  # Debugging if the button is clicked
    filter_value = filter_value_entry.get().strip()
    filter_column = filter_column_var.get()

    print(f"Original Filter Value (without strip): '{filter_value_entry.get()}'")
    print(f"Filter Value (after strip): '{filter_value}'")
    print(f"Selected Filter Column: '{filter_column}'")

    if not filter_value:
        messagebox.showinfo("Info", "No filter value entered. Showing all records.")
        refresh_treeview(tree, table)
    else:
        refresh_treeview(tree, table, filter_column, filter_value)

# GUI Setup
root = tk.Tk()
root.title("Bookstore Management System")
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

tables = {
    'Books': ['id', 'author_first_name', 'author_last_name', 'book_title', 'genre', 'publication_date', 'price', 'isbn', 'city_tax_denver', 'state_tax_co', 'total_price_incl_tax', 'image'],
    'Customer_Orders': ['order_id', 'customer_id', 'book_title', 'quantity_sold', 'order_status', 'order_date'],
    'Customers': ['customer_id', 'name', 'email', 'phone'],
    'Manufacturer_Orders': ['order_id', 'book_id', 'order_quantity', 'order_date', 'status'],
    'Sales': ['sale_id', 'book_id', 'quantity_sold', 'quantity_on_hand', 'remaining_quantity', 'total_price', 'sale_date', 'tracking_number', 'order_id', 'customer_name', 'payment_method'],
    'Users': ['user_id', 'name', 'email', 'password', 'created_at']
}

trees = {}
entries = {}

# Create tabs for each table
for table, columns in tables.items():
    frame = ttk.Frame(notebook)
    notebook.add(frame, text=table)

    # Create treeview for displaying data
    tree = ttk.Treeview(frame, columns=columns, show='headings')
    for col in columns:
        tree.heading(col, text=col)
    tree.pack(fill='both', expand=True)
    trees[table] = tree

    # Create input fields for adding new data
    input_frame = tk.Frame(frame)
    input_frame.pack(pady=10)
    entries[table] = {}

    for i, column in enumerate(columns):
        tk.Label(input_frame, text=column).grid(row=i, column=0, padx=5, pady=2, sticky="w")
        entry = tk.Entry(input_frame)
        entry.grid(row=i, column=1, padx=5, pady=2)
        entries[table][column] = entry

    # Add button to insert data (using threading to prevent UI freeze)
    tk.Button(frame, text=f"Add {table[:-1]}", command=lambda t=table: add_entry_threaded(t, {col: entries[t][col].get() for col in tables[t]})).pack(pady=5)

    # Add delete button with selection debugging
    tk.Button(frame, text=f"Delete {table[:-1]}",
          command=lambda t=table, tree=tree: delete_entry(t, tree.selection())).pack(pady=5)

    # Create a filter section
    filter_frame = tk.Frame(frame)
    filter_frame.pack(pady=5)

    # Add a dropdown for filter column selection
    filter_column_label = tk.Label(filter_frame, text="Filter by:")
    filter_column_label.grid(row=0, column=0, padx=5)
    
    filter_column_var = tk.StringVar()
    filter_column_var.set(columns[0])  # Default to the first column
    filter_column_dropdown = ttk.Combobox(filter_frame, textvariable=filter_column_var, values=columns)
    filter_column_dropdown.grid(row=0, column=1, padx=5)

    # Add an entry for the filter value
    filter_value_entry = tk.Entry(filter_frame)
    filter_value_entry.grid(row=0, column=2, padx=5)

    # Add button to apply filter
    filter_button = tk.Button(filter_frame, text="Apply Filter", 
                             command=lambda t=table, tree=tree, fve=filter_value_entry, fcv=filter_column_var: 
                             apply_filter(tree, t, fve, fcv))
    filter_button.grid(row=0, column=3, padx=5)

    # Add an image display label (only for the Books table)
    if table == "Books":
        image_label = tk.Label(frame)
        image_label.pack(pady=10)

        # Bind the row selection event to populate input fields and display the image
        tree.bind("<<TreeviewSelect>>", lambda event, tree=tree, table=table, image_label=image_label: on_treeview_select(event, tree, table, image_label))

    # Initial data load
    refresh_treeview(tree, table)

# Initialize tables
create_tables()
root.mainloop()