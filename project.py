import tkinter as tk
from tkinter import ttk, messagebox
import csv
import datetime
import os

class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management")

        self.products = {}
        self.product_names = self.load_product_names()

        self.last_scanned = []

        # Warehouse Entry
        self.warehouse_label = ttk.Label(root, text="Warehouse:")
        self.warehouse_label.grid(row=0, column=0, padx=10, pady=0, sticky=tk.W)

        self.warehouse_entry = ttk.Entry(root, width=2)
        self.warehouse_entry.grid(row=0, column=0, padx=125, pady=0, sticky=tk.W)

        # Barcode Entry
        self.barcode_label = ttk.Label(root, text="Barcode:")
        self.barcode_label.grid(row=1, column=0, padx=10, pady=0, sticky=tk.W)

        self.barcode_entry = ttk.Entry(root, width=10)
        self.barcode_entry.grid(row=1, column=0, padx=125, pady=0, sticky=tk.W)

        # Listbox
        self.product_listbox = tk.Listbox(root, height=10, width=60)
        self.product_listbox.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W)

        # Export Button
        self.export_button = ttk.Button(root, text="Export Inventory (CSV)", command=self.export_csv)
        self.export_button.grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)

        # Bindings
        self.barcode_entry.bind('<Return>', self.scan_product)

    def load_product_names(self):
        product_names = {}
        try:
            with open("products.csv", mode="r", newline="") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    barcode = row.get("Barcode", "").strip().lower()
                    product_name = row.get("Product Name", "").strip()
                    product_cost = row.get("Cost", "").strip()
                    if barcode and product_name:
                        product_names[barcode] = product_name
        except FileNotFoundError:
            messagebox.showwarning("Error", "File products.csv not found. The application will exit.")
            exit()

        return product_names

    def scan_product(self, event):
        warehouse = self.warehouse_entry.get().strip()
        barcode = self.barcode_entry.get().strip().lower()

        if not warehouse:
            messagebox.showwarning("Warehouse Missing", "Please enter the warehouse before scanning.")
            self.barcode_entry.delete(0, tk.END)  # Clear the barcode entry
            return

        if barcode:
            if barcode in self.products:
                self.products[barcode] += 1
            else:
                self.products[barcode] = 1

            if barcode not in self.product_names:
                product_name = self.get_product_name(barcode)
                self.product_names[barcode] = product_name

            product_name = self.product_names.get(barcode, "Unknown Product")
            entry = f"{product_name} - Barcode: {barcode} - Quantity: {self.products[barcode]} - Warehouse: {warehouse}"
            self.last_scanned.insert(0, entry)  # Insert at the beginning to keep the most recent at the top

            self.update_listbox()

            self.barcode_entry.delete(0, tk.END)

    def update_listbox(self):
        self.product_listbox.delete(0, tk.END)
        for entry in self.last_scanned:
            self.product_listbox.insert(tk.END, entry)

    def get_product_name(self, barcode):
        with open("products.csv", mode="r", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row.get("Barcode", "").strip().lower() == barcode:
                    return row.get("Product Name", "").strip()

        return "Unknown Product"

    def export_csv(self):
        warehouse = self.warehouse_entry.get().strip()
        if not warehouse:
            messagebox.showwarning("Warehouse Missing", "Please enter the warehouse before exporting.")
            return

        suffix = datetime.datetime.now().strftime("_%d%m%Y_%Hh%Mm")
        filename = f"inventory{suffix}.csv"

        with open(filename, mode="w", newline="") as file:
            fieldnames = ["Warehouse", "Barcode", "Product Name", "Quantity"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            writer.writeheader()

            for barcode, quantity in self.products.items():
                product_name = self.product_names.get(barcode, "Unknown Product")
                writer.writerow({"Warehouse": warehouse, "Barcode": barcode, "Product Name": product_name, "Quantity": quantity})

            print(f"CSV exported successfully as {filename}!")

if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()
