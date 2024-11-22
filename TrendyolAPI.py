import sys
import requests
from datetime import datetime, timezone
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QDateEdit, QMessageBox
import mysql.connector
import pytz
from datetime import datetime, timedelta, timezone

class TrendyolAPIApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Trendyol Order Processing")
        self.setGeometry(100, 100, 800, 600)

        # Layout
        self.layout = QVBoxLayout()
        self.form_layout = QHBoxLayout()

        # Start Date and End Date inputs
        self.start_date = QDateEdit(self)
        self.end_date = QDateEdit(self)
        self.start_date.setDate(datetime.today().date())  # Default to today
        self.end_date.setDate(datetime.today().date())  # Default to today

        self.form_layout.addWidget(self.start_date)
        self.form_layout.addWidget(self.end_date)

        # Dropdown menu for API Key and Seller ID
        self.api_dropdown = QComboBox(self)
        self.api_dropdown.addItem("Velours Violet")  # The name that will be displayed in the dropdown
        self.api_dropdown.addItem("Another Seller")  # You can add other sellers here as needed
        self.form_layout.addWidget(self.api_dropdown)

        # Button to process orders
        self.process_button = QPushButton("Process Orders", self)
        self.process_button.clicked.connect(self.process_orders)

        # Add the form layout and button to the main layout
        self.layout.addLayout(self.form_layout)
        self.layout.addWidget(self.process_button)

        # Table for displaying data
        self.table = QTableWidget(self)
        self.table.setColumnCount(4)  # 3 columns for Order Date, Merchant SKU, and Quantity
        self.table.setHorizontalHeaderLabels(["Order Date", "Merchant SKU", "Quantity", "Açıklama"])
        self.layout.addWidget(self.table)

        # Set the main layout
        self.setLayout(self.layout)

    def process_orders(self):
        # Get start and end date from the user input
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")

        # Get selected API Key and Seller ID from dropdown
        selected_option = self.api_dropdown.currentText()

        if selected_option == "Velours Violet":
            api_key = "alJxU3VMSDhYTmZ3NFhlSXhCOWc6b0xITG9ocjU2Z0NjZ25Hd1ppVGI="
            seller_id = "595149"
        else:
            # You can handle other sellers here if you add more items to the dropdown
            QMessageBox.critical(self, "Error", "Selected option is not available.")
            return

        # If start and end dates are the same, use the same timestamp for both
        if start_date == end_date:
            start_timestamp = self.convert_to_timestamp(start_date, start_of_day=True)
            end_timestamp = start_timestamp + 86400000 - 1  # Add 1 day minus 1ms (end of the same day)
        else:
            start_timestamp = self.convert_to_timestamp(start_date, start_of_day=True)
            end_timestamp = self.convert_to_timestamp(end_date, start_of_day=False)

        # Call API to fetch orders
        url = f"https://api.trendyol.com/sapigw/suppliers/{seller_id}/orders"
        headers = {"Authorization": f"Basic {api_key}", "User-Agent": "200300444 - Trendyolsoft"}

        # API call and data processing
        order_details = self.fetch_orders(url, headers, start_timestamp, end_timestamp)

        if not order_details:
            QMessageBox.warning(self, "No Orders", "No orders found for the selected date range.")
            return

        # Update table with order details
        self.update_table(order_details, selected_option)

        # After updating the table, you can now send the data to MySQL
        self.send_to_database(order_details)

    def convert_to_timestamp(self, date_str, start_of_day=True):
        # Set timezone to UTC+3 (Turkey)
        tz = pytz.timezone('Europe/Istanbul')

        # Convert the date string to a datetime object
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")

        # Adjust the time for the start of the day or the end of the day
        if start_of_day:
            date_obj = date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            date_obj = date_obj.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Localize the datetime object to UTC+3
        localized_date = tz.localize(date_obj, is_dst=None)

        # Convert the localized datetime to a timestamp
        return int(localized_date.timestamp() * 1000)  # In milliseconds

    def fetch_orders(self, url, headers, start_timestamp, end_timestamp):
        # Query parameters
        params = {"startDate": start_timestamp, "endDate": end_timestamp, "status": "Shipped", "page": 0, "size": 50}
        order_details = []

        while True:
            response = requests.get(url, headers=headers, params=params)

            # Print the full response for debugging
            print(f"API Response Status: {response.status_code}")
            if response.status_code == 200:
                response_data = response.json()

                # Debugging: print response data to check if any orders are returned
                print(f"API Response Data: {response_data}")

                for order in response_data.get("content", []):
                    order_date_unix = order.get("orderDate")
                    order_date = self.format_order_date(order_date_unix)
                    for line in order.get("lines", []):
                        merchant_sku = line.get("merchantSku")
                        quantity = line.get("quantity")
                        order_details.append([order_date, merchant_sku, quantity])

                total_pages = response_data.get("totalPages", 0)
                if params["page"] + 1 >= total_pages:
                    break
                params["page"] += 1
            else:
                # Error handling: print out the error message if status code is not 200
                print(f"Error: {response.status_code}, Response Text: {response.text}")
                break

        return order_details

    def format_order_date(self, unix_timestamp):
        return datetime.fromtimestamp(unix_timestamp / 1000, timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

    def update_table(self, order_details, selected_option):
        # Clear the existing table
        self.table.setRowCount(0)

        # Add data to the table
        for order in order_details:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)

            self.table.setItem(row_position, 0, QTableWidgetItem(order[0]))
            self.table.setItem(row_position, 1, QTableWidgetItem(order[1]))
            self.table.setItem(row_position, 2, QTableWidgetItem(str(order[2])))
            self.table.setItem(row_position, 3, QTableWidgetItem(selected_option))

    def send_to_database(self, order_details):
        connection = mysql.connector.connect(host="localhost", user="root", password="db_password", database="db_name")
        cursor = connection.cursor()
        selected_option = self.api_dropdown.currentText()
        primary_table = "satış_ürünlerim"
        secondary_table = "raf_ürünlerim"
        primary_log_table = "satış_hareketlerim"
        secondary_log_table = "raf_hareketlerim"

        for order in order_details:
            order_date = order[0]
            merchant_sku = order[1]
            quantity = order[2]

            insert_primary_log = f"""
            INSERT INTO {primary_log_table} (Tarih, Stok_Kodu, Stok, `Giriş/Çıkış`, Açıklama)
            VALUES (%s, %s, %s, 'Giriş', '{selected_option}')
            """
            cursor.execute(insert_primary_log, (order_date, merchant_sku, quantity))

            update_primary = f"""
            UPDATE {primary_table}
            SET Stok = IFNULL(Stok, 0) + %s
            WHERE Stok_Kodu = %s
            """
            cursor.execute(update_primary, (quantity, merchant_sku))

            update_secondary = f"""
            UPDATE {secondary_table}
            SET Stok = IFNULL(Stok, 0) - %s
            WHERE Stok_Kodu = %s
            """
            cursor.execute(update_secondary, (quantity, merchant_sku))

            insert_secondary_log = f"""
            INSERT INTO {secondary_log_table} (Tarih, Stok_Kodu, Stok, `Giriş/Çıkış`, Açıklama)
            VALUES (%s, %s, %s, 'Çıkış', '{selected_option}')
            """
            cursor.execute(insert_secondary_log, (order_date, merchant_sku, quantity))

        connection.commit()
        cursor.close()
        connection.close()

        print("Orders processed and added to the database.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TrendyolAPIApp()
    window.show()
    sys.exit(app.exec_())