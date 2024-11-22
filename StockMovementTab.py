from PyQt5.QtWidgets import QTabWidget, QVBoxLayout, QComboBox, QPushButton, QWidget, QFileDialog, QLabel, QMessageBox, QApplication
import pandas as pd
import mysql.connector


def fetch_timestamps():
    try:
        # Establish Database Connection
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="db_password",
            database="db_name"
        )
        cursor = connection.cursor()

        # Query to fetch distinct timestamps
        cursor.execute("SELECT DISTINCT timestamp FROM stock_audit ORDER BY timestamp DESC")
        timestamps = cursor.fetchall()

        # Format timestamps as string (datetime -> string)
        formatted_timestamps = [timestamp[0].strftime("%Y-%m-%d %H:%M:%S") for timestamp in timestamps]
        return formatted_timestamps

    except Exception as e:
        QMessageBox.critical(None, "Error", f"An error occurred while fetching timestamps: {e}")
        return []

    finally:
        cursor.close()
        connection.close()


def revert_stock(timestamp):
    try:
        # Establish Database Connection
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="db_password",
            database="db_name"
        )
        cursor = connection.cursor()

        # Get audit data for the selected timestamp
        query = f"""
        SELECT table_name, Stok_Kodu, old_stock
        FROM stock_audit
        WHERE timestamp = %s
        """
        cursor.execute(query, (timestamp,))
        audit_data = cursor.fetchall()

        # Revert stock values in the corresponding tables
        for row in audit_data:
            table_name, stock_code, old_stock = row
            update_query = f"""
            UPDATE {table_name}
            SET Stok = %s
            WHERE Stok_Kodu = %s
            """
            cursor.execute(update_query, (old_stock, stock_code))

        # Commit Changes
        connection.commit()
        QMessageBox.information(None, "Success", "Stock values have been reverted successfully.")

    except Exception as e:
        QMessageBox.critical(None, "Error", f"An error occurred while reverting stock: {e}")

    finally:
        cursor.close()
        connection.close()


def process_excel(file_path, selected_option):
    try:
        # Load Excel File
        sheet_name = "Stok Hareketleri"  # Replace with your sheet name
        df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl', skiprows=5, header=None)

        # Extract Columns
        column_data_tarih = df.iloc[:, 2]  # Column 3 (Tarih)
        column_data_stok_kodu = df.iloc[:, 3]  # Column 4 (Stok_Kodu)
        column_data_stok_adedi = df.iloc[:, 4]  # Column 5 (Stok)
        column_data_stok_hareketi = ["Giriş"] * len(column_data_stok_kodu)  # Column 6 (Giriş/Çıkış)
        column_data_açıklama = df.iloc[:, 6]  # Column 7 (Açıklama)

        # Filter Out Rows with NaN Values in Key Columns
        valid_data = df[~column_data_tarih.isna() & ~column_data_stok_kodu.isna() & ~column_data_stok_adedi.isna()]

        # Establish Database Connection
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="db_password",
            database="db_name"
        )
        cursor = connection.cursor()

        # Map options to table names
        table_mappings = {
            "Modelhane": ("modelhane_ürünlerim", "atölye_ürünlerim", "modelhane_hareketlerim", "atölye_hareketlerim"),
            "Atölye": ("atölye_ürünlerim", "modelhane_ürünlerim", "atölye_hareketlerim", "modelhane_hareketlerim"),
            "Katsız Depo": ("katsız_ürünlerim", "modelhane_ürünlerim", "katsız_hareketlerim", "modelhane_hareketlerim"),
            "Katlı Depo": ("katlı_ürünlerim", "katsız_ürünlerim", "katlı_hareketlerim", "katsız_hareketlerim"),
            "Raf": ("raf_ürünlerim", "katlı_ürünlerim", "raf_hareketlerim", "katlı_hareketlerim"),
            "Satış": ("satış_ürünlerim", "raf_ürünlerim", "satış_hareketlerim", "raf_hareketlerim")
        }

        if selected_option not in table_mappings:
            QMessageBox.critical(None, "Error", "Invalid option selected.")
            return

        primary_table, secondary_table, primary_log_table, secondary_log_table = table_mappings[selected_option]

        # Update Tables and Log Movements
        for _, row in valid_data.iterrows():
            tarih = row.iloc[2]
            stok_kodu = row.iloc[3]
            stok = row.iloc[4]
            açıklama = row.iloc[6] if pd.notna(row.iloc[6]) else ""  # Handle empty "Açıklama" by assigning an empty string

            # Skip if any value is None or NaN
            if pd.isna(tarih) or pd.isna(stok_kodu) or pd.isna(stok): 
                continue
            
            try:
                # Increase Stock in the primary table
                if selected_option == "Atölye":
                    update_primary = f"""
                    UPDATE {primary_table}
                    SET Stok = IFNULL(Stok, 0) + %s
                    WHERE Stok_Kodu = %s
                    """
                    cursor.execute(update_primary, (stok, stok_kodu))

                    insert_primary_log = f"""
                    INSERT INTO {primary_log_table} (Tarih, Stok_Kodu, Stok, `Giriş/Çıkış`, Açıklama)
                    VALUES (%s, %s, %s, 'Giriş', %s)
                    """
                    cursor.execute(insert_primary_log, (tarih, stok_kodu, stok, açıklama))
                else:
                    update_primary = f"""
                    UPDATE {primary_table}
                    SET Stok = IFNULL(Stok, 0) + %s
                    WHERE Stok_Kodu = %s
                    """
                    cursor.execute(update_primary, (stok, stok_kodu))
        
                    # Decrease Stock in the secondary table
                    update_secondary = f"""
                    UPDATE {secondary_table}
                    SET Stok = IFNULL(Stok, 0) - %s
                    WHERE Stok_Kodu = %s
                    """
                    cursor.execute(update_secondary, (stok, stok_kodu))
        
                    # Log "Çıkış" in the secondary log table
                    insert_secondary_log = f"""
                    INSERT INTO {secondary_log_table} (Tarih, Stok_Kodu, Stok, `Giriş/Çıkış`, Açıklama)
                    VALUES (%s, %s, %s, 'Çıkış', %s)
                    """
                    cursor.execute(insert_secondary_log, (tarih, stok_kodu, stok, açıklama))
        
                    # Log "Giriş" in the primary log table
                    insert_primary_log = f"""
                    INSERT INTO {primary_log_table} (Tarih, Stok_Kodu, Stok, `Giriş/Çıkış`, Açıklama)
                    VALUES (%s, %s, %s, 'Giriş', %s)
                    """
                    cursor.execute(insert_primary_log, (tarih, stok_kodu, stok, açıklama))

            except mysql.connector.Error as e:
                if e.errno == 1452:  # Foreign key violation
                    QMessageBox.critical(
                        None, "Foreign Key Error",
                        f"Error with Stok_Kodu: {stok_kodu}\nÜrünlerim dosyasında bu stok kodu yok bilo, Yeni Ürün kısmından ekle."
                    )
                    continue  # Skip to the next row
                else:
                    raise  # Re-raise other exceptions

        # Commit Changes
        connection.commit()
        QMessageBox.information(None, "Success", "Stock movements processed successfully.")

    except Exception as e:
        QMessageBox.critical(None, "Error", f"An error occurred: {e}")

    finally:
        # Close Database Connection
        cursor.close()
        connection.close()

# Create the tab widget for Stock Movement
class StockMovementTab(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Stock Movement Processor")
        self.setGeometry(100, 100, 400, 300)

        # Layout
        layout = QVBoxLayout()

        # Dropdown Menu for Options
        self.label = QLabel("Select Option:")
        layout.addWidget(self.label)
        self.dropdown = QComboBox()
        self.dropdown.addItems(["Atölye", "Modelhane", "Katsız Depo", "Katlı Depo", "Raf", "Satış"])
        layout.addWidget(self.dropdown)

        # File Selection Button
        self.file_button = QPushButton("Select Excel File")
        self.file_button.clicked.connect(self.select_file)
        layout.addWidget(self.file_button)

        # Revert Dropdown for Timestamps
        self.revert_label = QLabel("Select Timestamp to Revert:")
        layout.addWidget(self.revert_label)
        self.revert_dropdown = QComboBox()
        timestamps = fetch_timestamps()
        self.revert_dropdown.addItems(timestamps if timestamps else ["No timestamps available"])
        layout.addWidget(self.revert_dropdown)

        # Revert Button
        self.revert_button = QPushButton("Revert Stock")
        self.revert_button.clicked.connect(self.revert_stock)
        layout.addWidget(self.revert_button)

        self.setLayout(layout)

    def select_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select Excel File", "", "Excel Files (*.xls *.xlsx *.xlsm)")

        if file_path:
            selected_option = self.dropdown.currentText()
            process_excel(file_path, selected_option)
        else:
            QMessageBox.warning(self, "Warning", "No file selected.")

    def revert_stock(self):
        timestamp = self.revert_dropdown.currentText()

        if timestamp == "No timestamps available":
            QMessageBox.warning(self, "Warning", "No timestamps available to revert.")
            return

        revert_stock(timestamp)


# Main GUI that includes the Stock Movement tab
class MainApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Main GUI with Stock Movement Tab")
        self.setGeometry(100, 100, 800, 600)

        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.addTab(StockMovementTab(), "Stock Movement")
        # Add other tabs if needed...
        # Layout for the main window
        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication([])
    window = MainApp()
    window.show()
    app.exec_()