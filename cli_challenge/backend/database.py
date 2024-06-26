import os.path
import sqlite3

from cli_challenge.backend.product import Product
from cli_challenge.backend.order import Order


class Database:
    # Tester Code that creates a sample database
    @staticmethod
    def create_db():
        # Connects to the Database
        connection = sqlite3.connect('../backend/cli.db')

        # cursor for database
        cursor = connection.cursor()

        # Create the table used for mapping order to products
        cursor.execute("""CREATE TABLE IF NOT EXISTS ORDERS_TO_PRODUCTS(
                            ORDER_ID INT,
                            PRODUCT_ID INT,
                            BUSHELS DOUBLE
                            )""")
        cursor.execute("INSERT INTO ORDERS_TO_PRODUCTS VALUES (64, 0, 8.7)")
        cursor.execute("INSERT INTO ORDERS_TO_PRODUCTS VALUES (123, 2, 16.34)")
        cursor.execute("INSERT INTO ORDERS_TO_PRODUCTS VALUES (64, 1, 5)")

        cursor.execute("""CREATE TABLE IF NOT EXISTS ORDERS_TO_INFO(
                            ORDER_ID INT,
                            ORDER_DATE TEXT,
                            STATUS INT,
                            COST DOUBLE,
                            REVENUE DOUBLE
                            )""")
        cursor.execute("""INSERT INTO ORDERS_TO_INFO (ORDER_ID, ORDER_DATE, STATUS, COST, REVENUE) 
                            VALUES (?, ?, ?, ?, ?)""", (64, "Feb 26 2019", 0, 350, 669))
        cursor.execute("""INSERT INTO ORDERS_TO_INFO (ORDER_ID, ORDER_DATE, STATUS, COST, REVENUE) 
                            VALUES (?, ?, ?, ?, ?)""", (123, "Feb 26 2019", 0, 250.98, 1760))

        connection.commit()
        connection.close()

    # Loads the SQL Database, grabbing the previously stored orders
    @staticmethod
    def load_database(path):
        if not os.path.exists(path):
            Database.create_db()
        connection = sqlite3.connect(path)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM ORDERS_TO_INFO")

        query = cursor.fetchall()

        orders_dict = {}
        for curr_order in query:
            ID = curr_order[0]
            DATE = curr_order[1]
            STATUS = curr_order[2]
            COST = curr_order[3]
            REVENUE = curr_order[4]
            orders_dict[ID] = order = Order(DATE, ID, COST, REVENUE, STATUS)
            if order.state == Order.DELIVERED:
                Order.TOTAL_PROFIT += order.profit()
        cursor.execute("SELECT * FROM ORDERS_TO_PRODUCTS")
        query = cursor.fetchall()
        for curr_order in query:
            ID = curr_order[0]
            PRODUCT_ID = curr_order[1]
            BUSHELS = curr_order[2]
            orders_dict[ID].items.append(Product(BUSHELS, PRODUCT_ID, Product.get_BPMT(curr_order[1])))

        connection.commit()
        connection.close()
        return [*orders_dict.values()]

    # Updates the status of the order in the database when it is changed
    @staticmethod
    def update_order_status(order: Order):
        connection = sqlite3.connect('../backend/cli.db')
        cursor = connection.cursor()
        cursor.execute(f"UPDATE ORDERS_TO_INFO SET STATUS={order.state} WHERE ORDER_ID={order.id}")
        connection.commit()
        connection.close()
