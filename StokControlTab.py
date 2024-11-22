from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
)
import mysql.connector


class StokControlTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stok Kontrol")
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)


        self.check_critical_stock()
        # Input fields for adding
        self.stok_kodu_input = QLineEdit()
        self.stok_kodu_input.setPlaceholderText("Enter Stok Kodu")
        self.layout.addWidget(self.stok_kodu_input)

        self.kritik_stok_input = QLineEdit()
        self.kritik_stok_input.setPlaceholderText("Enter Kritik Stok")
        self.layout.addWidget(self.kritik_stok_input)

        # Submit button for adding
        self.submit_button = QPushButton("Add to Stok Kontrol")
        self.submit_button.clicked.connect(self.add_stok_kontrol)
        self.layout.addWidget(self.submit_button)

        # Input field for deleting
        self.delete_stok_kodu_input = QLineEdit()
        self.delete_stok_kodu_input.setPlaceholderText("Enter Stok Kodu to Delete")
        self.layout.addWidget(self.delete_stok_kodu_input)

        # Delete button
        self.delete_button = QPushButton("Delete from Stok Kontrol")
        self.delete_button.clicked.connect(self.delete_stok_kontrol)
        self.layout.addWidget(self.delete_button)

        # Display table
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Stok Kodu", "Kritik Stok"])
        self.layout.addWidget(self.table)

        # Load existing data
        self.load_data()

    def add_stok_kontrol(self):
        stok_kodu = self.stok_kodu_input.text().strip()
        kritik_stok = self.kritik_stok_input.text().strip()

        if not stok_kodu or not kritik_stok.isdigit():
            QMessageBox.warning(self, "Input Error", "Please enter valid Stok Kodu and Kritik Stok.")
            return

        # Database connection
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="db_password",
            database="db_name"
        )
        cursor = connection.cursor()

        try:
            # Insert data into the table with NULL for Uyarı
            query = "INSERT INTO stok_kontrol (Stok_Kodu, kritik_stok, Uyarı) VALUES (%s, %s, %s)"
            cursor.execute(query, (stok_kodu, int(kritik_stok), None))  # Use None for NULL
            connection.commit()

            # Run check_critical_stock to update Uyarı column
            self.check_critical_stock()

            QMessageBox.information(self, "Success", "Data added successfully.")
            self.load_data()  # Refresh table
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")
        finally:
            cursor.close()
            connection.close()
            
    def delete_stok_kontrol(self):
        stok_kodu = self.delete_stok_kodu_input.text().strip()

        if not stok_kodu:
            QMessageBox.warning(self, "Input Error", "Please enter a valid Stok Kodu.")
            return

        # Database connection
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="db_password",
            database="db_name"
        )
        cursor = connection.cursor()

        try:
            # Delete the row from the table
            query = "DELETE FROM stok_kontrol WHERE Stok_Kodu = %s"
            cursor.execute(query, (stok_kodu,))
            connection.commit()

            if cursor.rowcount > 0:
                QMessageBox.information(self, "Success", "Row deleted successfully.")
            else:
                QMessageBox.warning(self, "Not Found", "No matching row found.")

            self.load_data()  # Refresh table
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")
        finally:
            cursor.close()
            connection.close()

    def load_data(self):
        # Clear existing rows
        self.table.setRowCount(0)
    
        # Database connection
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="db_password",
            database="db_name"
        )
        cursor = connection.cursor()
    
        try:
            # Fetch data
            query = "SELECT Stok_Kodu, kritik_stok, Uyarı FROM stok_kontrol"
            cursor.execute(query)
            rows = cursor.fetchall()
    
            self.table.setColumnCount(3)  # Update column count
            self.table.setHorizontalHeaderLabels(["Stok Kodu", "Kritik Stok", "Uyarı"])  # Add new header
    
            for row_data in rows:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(row_data[0]))
                self.table.setItem(row, 1, QTableWidgetItem(str(row_data[1])))
                self.table.setItem(row, 2, QTableWidgetItem(row_data[2] if row_data[2] else ""))
    
            # Adjust the width of the Uyarı column (index 2)
            self.table.setColumnWidth(2, 300)  # Adjust the width as needed (e.g., 300 pixels)
    
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")
        finally:
            cursor.close()
            connection.close()

    def check_critical_stock(self):
        # Database connection
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="db_password",
            database="db_name"
        )
        cursor = connection.cursor()

        try:
            # Fetch all Stok_Kodu and kritik_stok from stok_kontrol table
            cursor.execute("SELECT Stok_Kodu, kritik_stok FROM stok_kontrol")
            stok_kontrol_rows = cursor.fetchall()

            for row in stok_kontrol_rows:
                stok_kodu = row[0]
                kritik_stok = row[1]

                # Fetch Stok from katlı_ürünlerim table for the same Stok_Kodu
                cursor.execute("SELECT Stok FROM katlı_ürünlerim WHERE Stok_Kodu = %s", (stok_kodu,))
                katlı_row = cursor.fetchone()

                if katlı_row:
                    stok_value = katlı_row[0]  # Get stok value from katlı_ürünlerim

                    # If stok_value from katlı_ürünlerim is lower than kritik_stok, check other tables
                    if stok_value < kritik_stok:
                        uyarı_message = f"Katlıda {stok_value} bulunmakta"

                        # Fetch Stok from katsız_ürünlerim table for the same Stok_Kodu
                        cursor.execute("SELECT Stok FROM katsız_ürünlerim WHERE Stok_Kodu = %s", (stok_kodu,))
                        katsız_row = cursor.fetchone()
                        if katsız_row:
                            uyarı_message += f", Katsız: {katsız_row[0]}"  # Add katsız_ürünlerim stok value to message

                        # Fetch Stok from modelhane_ürünlerim table for the same Stok_Kodu
                        cursor.execute("SELECT Stok FROM modelhane_ürünlerim WHERE Stok_Kodu = %s", (stok_kodu,))
                        atölye_row = cursor.fetchone()
                        if atölye_row:
                            uyarı_message += f", Modelhane: {atölye_row[0]}"  # Add modelhane_ürünlerim stok value to message

                        cursor.execute("SELECT Stok FROM atölye_ürünlerim WHERE Stok_Kodu = %s", (stok_kodu,))
                        atölye_row = cursor.fetchone()
                        if atölye_row:
                            uyarı_message += f", Atölye: {atölye_row[0]}"  # Add atölye_ürünlerim stok value to message

                        # Update Uyarı column in stok_kontrol table
                        cursor.execute(
                            "UPDATE stok_kontrol SET Uyarı = %s WHERE Stok_Kodu = %s",
                            (uyarı_message, stok_kodu)
                        )
                        connection.commit()

            QMessageBox.information(self, "Success", "Stock check completed and Uyarı updated where necessary.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")
        finally:
            cursor.close()
            connection.close()