import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget, QPushButton, QFileDialog, QMessageBox, QDateEdit
from PyQt5.QtCore import QDate
import mysql.connector
import pandas as pd
from StockMovementTab import StockMovementTab
from ProductEntry import ProductEntryWindow
from StokControlTab import StokControlTab
import openpyxl
from TrendyolAPI import TrendyolAPIApp
from ManuelDüzeltme import StockCorrectionApp

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bilo Depo")
        self.setGeometry(100, 100, 600, 400)

        # Set up QTabWidget to hold multiple tabs
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Existing tab (your current code)
        self.existing_tab = QWidget()
        self.existing_tab_layout = QVBoxLayout()
        self.existing_tab.setLayout(self.existing_tab_layout)

        # New tab (StockMovementTab)
        self.new_tab = StockMovementTab()
        self.tabs.addTab(self.existing_tab, "Excel İndir")
        self.tabs.addTab(self.new_tab, "Stok Hareketleri")

        self.trendyol_api_tab = TrendyolAPIApp()  # Instantiate the TrendyolAPIApp class
        self.tabs.addTab(self.trendyol_api_tab, "Trendyol Siparişleri")

        self.product_entry_window = ProductEntryWindow()
        self.tabs.addTab(self.product_entry_window, "Yeni Ürün")

        # Add Stok Kontrol Tab
        self.stok_control_tab = StokControlTab()
        self.tabs.addTab(self.stok_control_tab, "Stok Kontrol")

        self.stok_control_tab = StockCorrectionApp()
        self.tabs.addTab(self.stok_control_tab, "Manuel Düzeltme")

        # Create Excel File Button
        self.create_button = QPushButton("Create Excel File from Database")
        self.create_button.clicked.connect(self.create_excel_file)
        self.existing_tab_layout.addWidget(self.create_button)

        self.date_picker = QDateEdit()
        self.date_picker.setDate(QDate.currentDate())
        self.existing_tab_layout.addWidget(self.date_picker)

        # Button for Fetching _hareketlerim Data
        self.fetch_button = QPushButton("Fetch Hareketlerim Data")
        self.fetch_button.clicked.connect(self.fetch_hareketlerim_data)
        self.existing_tab_layout.addWidget(self.fetch_button)

    def create_excel_file(self):
        # Database connection
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="db_password",
            database="db_name"
        )
        cursor = connection.cursor()

        try:
            # Fetch all table names
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()

            # Create a Pandas Excel writer object
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getSaveFileName(self, "Save Excel File", "", "Excel Files (*.xlsx)")

            if file_path:
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    # Write each table to a separate sheet
                    for table in tables:
                        table_name = table[0]
                        cursor.execute(f"SELECT * FROM {table_name}")
                        rows = cursor.fetchall()

                        if rows and cursor.description:
                            columns = [desc[0] for desc in cursor.description]
                            df = pd.DataFrame(rows, columns=columns)
                            df.to_excel(writer, sheet_name=table_name, index=False)

                    # Data for Atölye_Modelhane
                    cursor.execute("SELECT Stok_Kodu, Stok FROM atölye_ürünlerim")
                    atolye_rows = cursor.fetchall()

                    cursor.execute("SELECT Stok_Kodu, Stok FROM modelhane_ürünlerim")
                    modelhane_rows = cursor.fetchall()

                    # Fetch data from other product tables
                    cursor.execute("SELECT Stok_Kodu, Stok FROM katsız_ürünlerim")
                    katsız_rows = cursor.fetchall()

                    cursor.execute("SELECT Stok_Kodu, Stok FROM katlı_ürünlerim")
                    katlı_rows = cursor.fetchall()

                    cursor.execute("SELECT Stok_Kodu, Stok FROM raf_ürünlerim")
                    raf_rows = cursor.fetchall()

                    cursor.execute("SELECT Stok_Kodu, Stok FROM satış_ürünlerim")
                    satış_rows = cursor.fetchall()

                    if atolye_rows or modelhane_rows or katsız_rows or katlı_rows or raf_rows or satış_rows:
                        # Prepare data for the new sheet
                        stok_kodlari = []
                        atolye_values = []
                        modelhane_values = []
                        katsız_values = []
                        katlı_values = []
                        raf_values = []
                        satış_values = []

                        # Convert rows to dictionaries for fast lookup
                        atolye_dict = {row[0]: row[1] for row in atolye_rows}
                        modelhane_dict = {row[0]: row[1] for row in modelhane_rows}
                        katsız_dict = {row[0]: row[1] for row in katsız_rows}
                        katlı_dict = {row[0]: row[1] for row in katlı_rows}
                        raf_dict = {row[0]: row[1] for row in raf_rows}
                        satış_dict = {row[0]: row[1] for row in satış_rows}

                        # Combine all Stok_Kodu keys
                        all_stok_kodlari = set(
                            atolye_dict.keys()
                        ).union(
                            modelhane_dict.keys(),
                            katsız_dict.keys(),
                            katlı_dict.keys(),
                            raf_dict.keys(),
                            satış_dict.keys()
                        )

                        for stok_kodu in all_stok_kodlari:
                            stok_kodlari.append(stok_kodu)
                            atolye_values.append(atolye_dict.get(stok_kodu, ''))
                            modelhane_values.append(modelhane_dict.get(stok_kodu, ''))
                            katsız_values.append(katsız_dict.get(stok_kodu, ''))
                            katlı_values.append(katlı_dict.get(stok_kodu, ''))
                            raf_values.append(raf_dict.get(stok_kodu, ''))
                            satış_values.append(satış_dict.get(stok_kodu, ''))

                        # Create DataFrame for Atölye_Modelhane
                        new_data = {
                            'Stok_Kodu': stok_kodlari,
                            'Atölye': atolye_values,
                            'Modelhane': modelhane_values,
                            'Katsız': katsız_values,
                            'Katlı': katlı_values,
                            'Raf': raf_values,
                            'Satış': satış_values,
                        }

                        new_df = pd.DataFrame(new_data)
                        new_df.to_excel(writer, sheet_name="Hepsi", index=False)

                workbook = openpyxl.load_workbook(file_path)

                for sheet_name in workbook.sheetnames:
                    sheet = workbook[sheet_name]
                    # Freeze the first column (column A)
                    sheet.freeze_panes = "A2"

                workbook.save(file_path)

                QMessageBox.information(self, "Success", "Excel file created successfully.")
            else:
                QMessageBox.warning(self, "Warning", "No file selected.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

        finally:
            cursor.close()
            connection.close()

    def fetch_hareketlerim_data(self):
        # Get the selected date from the date picker
        selected_date = self.date_picker.date().toString("yyyy-MM-dd")
        
        # Database connection
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="db_password",
            database="db_nname"
        )
        cursor = connection.cursor()

        try:
            # Fetch all _hareketlerim tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()

            # Filter tables with '_hareketlerim' in their name
            hareketlerim_tables = [table[0] for table in tables if "_hareketlerim" in table[0]]

            if not hareketlerim_tables:
                QMessageBox.warning(self, "Warning", "No _hareketlerim tables found in the database.")
                return

            # Initialize a dictionary to store the filtered data for each table
            filtered_data = {}

            for table in hareketlerim_tables:
                query = f"SELECT * FROM {table} WHERE `Tarih` = %s"
                cursor.execute(query, (selected_date,))
                rows = cursor.fetchall()

                # Check if cursor returned any rows and handle it properly
                if rows:
                    columns = [desc[0] for desc in cursor.description]
                    filtered_data[table] = pd.DataFrame(rows, columns=columns)

            # Check if there is data for the selected date
            if not filtered_data:
                QMessageBox.warning(self, "No Data", "No data found for the selected date.")
            else:
                # Optionally, you can export the filtered data to an Excel file here or show it in a GUI
                # For example, let's create an Excel file for the filtered data
                file_dialog = QFileDialog()
                file_path, _ = file_dialog.getSaveFileName(self, "Save Filtered Data", "", "Excel Files (*.xlsx)")

                if file_path:
                    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                        for table, data in filtered_data.items():
                            data.to_excel(writer, sheet_name=table, index=False)
                    QMessageBox.information(self, "Success", "Filtered data saved to Excel successfully.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

        finally:
            cursor.close()
            connection.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


#C:\Users\ahmet\output