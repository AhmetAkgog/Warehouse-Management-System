from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QComboBox, QPushButton, QLabel, QLineEdit, QMessageBox, QApplication
)
import mysql.connector
from datetime import datetime


class StockCorrectionApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Stock Correction")
        self.setGeometry(100, 100, 400, 300)

        # Layout
        layout = QVBoxLayout()

        # Dropdown Menu for Table Selection
        self.label_table = QLabel("Select Table:")
        layout.addWidget(self.label_table)

        self.dropdown_table = QComboBox()
        self.dropdown_table.addItems(["atölye_ürünlerim", "modelhane_ürünlerim", "katsız_ürünlerim", 
                                       "katlı_ürünlerim", "raf_ürünlerim", "satış_ürünlerim"])
        layout.addWidget(self.dropdown_table)

        # Input for Stok_Kodu
        self.label_stok_kodu = QLabel("Enter Stok_Kodu:")
        layout.addWidget(self.label_stok_kodu)

        self.input_stok_kodu = QLineEdit()
        layout.addWidget(self.input_stok_kodu)

        # Input for New Stok Value
        self.label_stok_value = QLabel("Enter New Stok Value:")
        layout.addWidget(self.label_stok_value)

        self.input_stok_value = QLineEdit()
        layout.addWidget(self.input_stok_value)

        # Submit Button
        self.submit_button = QPushButton("Update Stock")
        self.submit_button.clicked.connect(self.update_stock)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def update_stock(self):
        # Get user input
        selected_table = self.dropdown_table.currentText()
        stok_kodu = self.input_stok_kodu.text()
        new_stok_value = self.input_stok_value.text()

        if not stok_kodu or not new_stok_value:
            QMessageBox.warning(self, "Warning", "Please fill all fields.")
            return

        try:
            # Establish Database Connection
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="db_password",
                database="db_name"
            )
            cursor = connection.cursor()

            # Derive the corresponding hareketlerim table
            hareketlerim_table = selected_table.replace("_ürünlerim", "_hareketlerim")

            # Update Stok in the selected table
            update_query = f"""
                UPDATE {selected_table}
                SET Stok = %s
                WHERE Stok_Kodu = %s
            """
            cursor.execute(update_query, (new_stok_value, stok_kodu))

            # Insert into the hareketlerim table
            insert_query = f"""
                INSERT INTO {hareketlerim_table} (Tarih, Stok_Kodu, Stok, `Giriş/Çıkış`, Açıklama)
                VALUES (%s, %s, %s, '', 'Stok Düzeltme')
            """
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(insert_query, (current_date, stok_kodu, new_stok_value))

            # Commit changes
            connection.commit()

            QMessageBox.information(self, "Success", "Stock updated and logged successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

        finally:
            # Close connection
            cursor.close()
            connection.close()


if __name__ == "__main__":
    app = QApplication([])
    window = StockCorrectionApp()
    window.show()
    app.exec_()