import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QPushButton, QCheckBox, QMessageBox
import mysql.connector


class ProductEntryWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Product Entry & Deletion")
        self.setGeometry(100, 100, 400, 350)

        # Layout for the product entry and deletion form
        self.product_entry_layout = QVBoxLayout()

        # Create form layout for product inputs
        self.product_form_layout = QFormLayout()

        # Input field for Stok_Kodu (no Stok field, it's set to 0 by default)
        self.stok_kodu_input = QLineEdit()
        self.product_form_layout.addRow("Stok Kodu:", self.stok_kodu_input)

        # ComboBox for selecting the product table (_ürünlerim)
        self.table_select_combo = QComboBox()
        self.table_select_combo.addItem("atölye_ürünlerim")
        self.table_select_combo.addItem("modelhane_ürünlerim")
        self.table_select_combo.addItem("katsız_ürünlerim")
        self.table_select_combo.addItem("katlı_ürünlerim")
        self.table_select_combo.addItem("raf_ürünlerim")
        self.table_select_combo.addItem("satış_ürünlerim")
        self.product_form_layout.addRow("Select Table:", self.table_select_combo)

        # Add form layout to the tab
        self.product_entry_layout.addLayout(self.product_form_layout)

        # Button to submit the product entry
        self.submit_button = QPushButton("Add Product")
        self.submit_button.clicked.connect(self.add_product)
        self.product_entry_layout.addWidget(self.submit_button)

        # Checkbox to add product to all _ürünlerim tables
        self.add_to_all_checkbox = QCheckBox("Add to all _ürünlerim tables")
        self.product_entry_layout.addWidget(self.add_to_all_checkbox)

        # Section for Deleting Product
        self.delete_form_layout = QFormLayout()

        # Input for Stok_Kodu to delete
        self.stok_kodu_delete_input = QLineEdit()
        self.delete_form_layout.addRow("Stok Kodu (Delete):", self.stok_kodu_delete_input)

        # Button to delete the product
        self.delete_button = QPushButton("Delete Product")
        self.delete_button.clicked.connect(self.delete_product)
        self.delete_form_layout.addRow(self.delete_button)

        # Add the delete section layout to the main layout
        self.product_entry_layout.addLayout(self.delete_form_layout)

        # Set the layout of the window
        self.setLayout(self.product_entry_layout)

    def add_product(self):
        # Get the Stok_Kodu from the input field
        stok_kodu = self.stok_kodu_input.text()

        if not stok_kodu:
            QMessageBox.warning(self, "Input Error", "Please enter the Stok Kodu.")
            return

        # Default Stok is 0
        stok = 0

        # Determine which tables to insert into
        table_name = self.table_select_combo.currentText()
        tables_to_insert = [table_name]

        # If "Add to all _ürünlerim tables" checkbox is selected, add to both tables
        if self.add_to_all_checkbox.isChecked():
            tables_to_insert = ["atölye_ürünlerim", "modelhane_ürünlerim","katsız_ürünlerim","katlı_ürünlerim","raf_ürünlerim","satış_ürünlerim"]

        # Database connection
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="db_password",
            database="db_name"
        )
        cursor = connection.cursor()

        try:
            # Insert the new product data into the selected tables
            insert_query = "INSERT INTO {table_name} (Stok_Kodu, Stok) VALUES (%s, %s)"
            for table_name in tables_to_insert:
                cursor.execute(insert_query.format(table_name=table_name), (stok_kodu, stok))
                connection.commit()

            # Inform the user that the product has been added
            QMessageBox.information(self, "Success", f"Product added to {', '.join(tables_to_insert)}.")

            # Clear the input field after submission
            self.stok_kodu_input.clear()
            self.add_to_all_checkbox.setChecked(False)  # Uncheck the checkbox after the operation

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")
            connection.rollback()

        finally:
            cursor.close()
            connection.close()

    def delete_product(self):
        # Get the Stok_Kodu for deletion
        stok_kodu_delete = self.stok_kodu_delete_input.text()

        if not stok_kodu_delete:
            QMessageBox.warning(self, "Input Error", "Please enter the Stok Kodu to delete.")
            return

        # Tables to delete from (always both tables)
        tables_to_delete = ["atölye_ürünlerim", "modelhane_ürünlerim","katsız_ürünlerim","katlı_ürünlerim","raf_ürünlerim","satış_ürünlerim"]

        # Database connection
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="db_password",
            database="db_name"
        )
        cursor = connection.cursor()

        try:
            # Delete the product data from the selected tables
            delete_query = "DELETE FROM {table_name} WHERE Stok_Kodu = %s"
            for table_name in tables_to_delete:
                cursor.execute(delete_query.format(table_name=table_name), (stok_kodu_delete,))
                connection.commit()

            # Inform the user that the product has been deleted
            QMessageBox.information(self, "Success", f"Product with Stok Kodu '{stok_kodu_delete}' deleted from {', '.join(tables_to_delete)}.")

            # Clear the input fields after deletion
            self.stok_kodu_delete_input.clear()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")
            connection.rollback()

        finally:
            cursor.close()
            connection.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProductEntryWindow()
    window.show()
    sys.exit(app.exec_())