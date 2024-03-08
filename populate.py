import sqlite3
import pandas as pd
import hashlib as hl
from datetime import datetime

#Used to has passwords for Users table
def hashVal(val):
    return hl.md5(val.encode()).hexdigest()

#Creates the tables for the database
def createDB():
    #Creates db file if it doesn't exist
    with open('database.db','a+'):
        pass

    connection = sqlite3.connect('database.db')
    cur = connection.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS Zipcode_info (
            zipcode INTEGER NOT NULL,
            city VARCHAR(64) NOT NULL,
            state_id CHAR(2) NOT NULL,
            population INTEGER,
            density REAL,
            county_name VARCHAR(64),
            timezone VARCHAR(64),
            PRIMARY KEY (zipcode)
        ) '''
    )

    cur.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            email VARCHAR(64),
            password CHAR(32),
            PRIMARY KEY(email)
        )'''
    )

    cur.execute(
        '''CREATE TABLE IF NOT EXISTS Address (
            address_id CHAR(32) NOT NULL,
            zipcode INTEGER NOT NULL,
            street_num INTEGER NOT NULL,
            street_name VARCHAR(64) NOT NULL,
            PRIMARY KEY (address_id),
            FOREIGN KEY (zipcode) REFERENCES Zipcode_info(zipcode)
        )'''
    )

    cur.execute(
        '''CREATE TABLE IF NOT EXISTS Buyers (
            email VARCHAR(64) NOT NULL,
            first_name VARCHAR(64) NOT NULL,
            last_name VARCHAR(64) NOT NULL,
            gender VARCHAR(64) NOT NULL,
            age INTEGER NOT NULL,
            home_address_id CHAR(32) NOT NULL,
            billing_address_id CHAR(32) NOT NULL,
            PRIMARY KEY (email),
            FOREIGN KEY (home_address_id) REFERENCES Address(address_id),
            FOREIGN KEY (billing_address_id) REFERENCES Address(address_id),
            FOREIGN KEY (email) REFERENCES Users (email)
        )'''
    )

    cur.execute(
        '''CREATE TABLE IF NOT EXISTS Credit_Cards (
            credit_card_num CHAR(19)NOT NULL,
            card_code INTEGER NOT NULL,
            expire_month INTEGER NOT NULL,
            expire_year INTEGER NOT NULL,
            card_type VARCHAR(64) NOT NULL,
            Owner_email VARCHAR(64) NOT NULL,
            PRIMARY KEY (credit_card_num),
            FOREIGN KEY (Owner_email) REFERENCES Buyers(email)
        )'''
    )

    cur.execute('''
        CREATE TABLE IF NOT EXISTS Sellers (
            email VARCHAR(64) NOT NULL,
            routing_number CHAR(11) NOT NULL,
            account_number INTEGER NOT NULL,
            balance INTEGER NOT NULL,
            PRIMARY KEY (email),
            FOREIGN KEY (email) REFERENCES Users(email)
        )'''
    )
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Local_Vendors (
            Email VARCHAR(64) NOT NULL,
            Business_Name VARCHAR(64) NOT NULL,
            Business_Address_ID CHAR(32) NOT NULL,
            Customer_Service_Number CHAR(13) NOT NULL,
            PRIMARY KEY (Email),
            FOREIGN KEY (Email) REFERENCES Sellers(email)
        )'''
    )

    cur.execute('''
        CREATE TABLE IF NOT EXISTS Categories (
            parent_category VARCHAR(64) NOT NULL,
            category_name VARCHAR(64) NOT NULL,
            PRIMARY KEY (category_name)
        )'''
    )

    cur.execute('''
        CREATE TABLE IF NOT EXISTS Product_Listing (
            Seller_Email VARCHAR(64) NOT NULL,
            Listing_ID INTEGER NOT NULL,
            Category VARCHAR(64) NOT NULL,
            Title VARCHAR(64) NOT NULL,
            Product_Name VARCHAR(64) NOT NULL,
            Product_Description VARCHAR(64) NOT NULL,
            Price VARCHAR(64) NOT NULL,
            Quantity INTEGER NOT NULL,
            Status INTEGER DEFAULT 1 NOT NULL,
            Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            PRIMARY KEY (Seller_Email, Listing_ID),
            FOREIGN KEY (Seller_Email) REFERENCES Sellers(email),
            FOREIGN KEY (Category) REFERENCES Categories(category_name)
        )'''
    )

    cur.execute('''
        CREATE TABLE IF NOT EXISTS Orders (
            Transaction_ID INTEGER NOT NULL,
            Seller_Email VARCHAR(64) NOT NULL,
            Listing_ID INTEGER NOT NULL,
            Buyer_Email VARCHAR(64) NOT NULL,
            Date DATE NOT NULL,
            Quantity INTEGER NOT NULL,
            Payment INTEGER NOT NULL,
            PRIMARY KEY (Transaction_ID),
            FOREIGN KEY (Buyer_Email) REFERENCES Buyers(email),
            FOREIGN KEY (Seller_Email,Listing_ID) REFERENCES Product_Listing(Seller_email,Listing_ID)
        )'''
    )

    cur.execute('''
        CREATE TABLE IF NOT EXISTS Reviews (
            Buyer_Email VARCHAR(64) NOT NULL,
            Seller_Email VARCHAR(64) NOT NULL,
            Listing_ID INTEGER NOT NULL,
            Review_Desc VARCHAR(64) NOT NULL,
            PRIMARY KEY (Buyer_Email, Seller_Email, Listing_ID),
            FOREIGN KEY (Buyer_Email) REFERENCES Buyers(email),
            FOREIGN KEY (Seller_Email,Listing_ID) REFERENCES Product_Listing(Seller_Email,Listing_ID)
        )'''
    )

    cur.execute('''
        CREATE TABLE IF NOT EXISTS Rating (
            Buyer_Email VARCHAR(64) NOT NULL,
            Seller_Email VARCHAR(64) NOT NULL,
            Date DATE NOT NULL,
            Rating INTEGER NOT NULL,
            Rating_Desc VARCHAR(64),
            PRIMARY KEY (Buyer_Email, Seller_Email, Date),
            FOREIGN KEY (Buyer_Email) REFERENCES Buyers(email),
            FOREIGN KEY (Seller_Email) REFERENCES Sellers(email)
        )'''
    )
    connection.commit()

#Populates the tables with datat from CSV files
def populate():
    con = sqlite3.connect('database.db')
    with open('dataset/Zipcode_Info.csv','r') as f:
        df = pd.read_csv(f)
        df.to_sql('Zipcode_info',con,if_exists="replace",index=False)

    with open('dataset/Users.csv','r') as f:
        df = pd.read_csv(f)
        df['password'] = df['password'].apply(hashVal) #Hash all passwords
        df.to_sql('Users',con,if_exists="replace",index=False)
        
    with open('dataset/Address.csv','r') as f:
        df = pd.read_csv(f)
        df.to_sql('Address',con,if_exists="replace",index=False)
    
    with open('dataset/Buyers.csv','r') as f:
        df = pd.read_csv(f)
        df.to_sql('Buyers',con,if_exists="replace",index=False)
    
    with open('dataset/Credit_Cards.csv','r') as f:
        df = pd.read_csv(f)
        df.to_sql('Credit_Cards',con,if_exists="replace",index=False)

    with open('dataset/Sellers.csv','r') as f:
        df = pd.read_csv(f)
        df.to_sql('Sellers',con,if_exists="replace",index=False)

    with open('dataset/Local_Vendors.csv','r') as f:
        df = pd.read_csv(f)
        df.to_sql('Local_Vendors',con,if_exists="replace",index=False) 

    with open('dataset/Categories.csv','r') as f:
        df = pd.read_csv(f)
        df.to_sql('Categories',con,if_exists="replace",index=False)

    with open('dataset/Product_Listing.csv','r') as f:
        df = pd.read_csv(f)
        df['Status'] = 1
        df['Timestamp'] = datetime.now().isoformat(timespec='seconds')
        df.to_sql('Product_Listing',con,if_exists="replace",index=False)

    with open('dataset/Orders.csv','r') as f:
        df = pd.read_csv(f)
        df.to_sql('Orders',con,if_exists="replace",index=False)

    with open('dataset/Reviews.csv','r') as f:
        df = pd.read_csv(f)
        df.to_sql('Reviews',con,if_exists="replace",index=False)

    with open('dataset/Ratings.csv','r') as f:
        df = pd.read_csv(f)
        df.to_sql('Rating',con,if_exists="replace",index=False)

    con.commit()

createDB()
populate()
print("Ran with no issues")
