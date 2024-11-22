# Warehouse-Management-System
Stock control system for a business with five different warehouses. I used Python, MySQL, MySQL connector,openpyxl for Excel transfers, and pyqt5 for the GUI.

Main.py: This tab can download the whole database or stock transfers between warehouses on a specific date.

![image](https://github.com/user-attachments/assets/6efb747e-1bc6-41c9-a9da-8bee822d0eae)

Stockmovementtab.py: This tab is responsible for stock movements, The user chooses a warehouse and uploads a transfer excel file for the appropriate warehouse. In case of wrong uploads user can revert the database based on timestamps.

![image](https://github.com/user-attachments/assets/6d892a56-52ed-4511-9d59-83c20b63a608)

TrendyolAPI.py: This tab gets the orders given to the cargo company based on the store(it needs an API key and seller_id) and on a specific date. It returns the date order created, the SKU of the product, Quantity and a Description for clearance in the database. Uploads the output to the satış_hareketlerim table.

![image](https://github.com/user-attachments/assets/e41536a2-9464-4f3e-905d-49701cd0102f)

ProductEntry.py: This tab is for uploading or deleting a product from the tables.

![image](https://github.com/user-attachments/assets/aa08cb9b-287f-4040-b15a-01024ade6053)

StokControlTab.py : User enters a merchant sku and the a critic stock level for alerting them incase it gets lower. If the entered merchant sku gets lower in the katlı_depo table, it will be displayed in this tab and will return the values of that merchant sku in the tables of katlı_ürünlerim, katsız_ürünlerim, modelhane_ürünlerim, atölye_ürünlerim.

![image](https://github.com/user-attachments/assets/24380f7b-405e-4e83-9c79-576236581624)

ManuelDüzeltme.py: In case of doing mistakes the users can change the stock values of the products in the chosen warehouses. This will be recorded in according the _hareketlerim tables as "STOK DÜZELTME".

![image](https://github.com/user-attachments/assets/e53fe38c-1e4f-414d-841b-7bce2d07b3c8)
