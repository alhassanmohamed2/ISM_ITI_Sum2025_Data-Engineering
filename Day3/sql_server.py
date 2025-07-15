import mysql.connector

config = {
    'host': 'localhost',
    'user': 'root',  
    'password': '',  
    'database': 'employees'
}

connection = mysql.connector.connect(**config)
cursor = connection.cursor(dictionary=True)


query = "SELECT * FROM employees limit 10"
cursor.execute(query)

rows = cursor.fetchall()

for row in rows:
    print(row["first_name"] + " "+row["last_name"])

for row in rows:
    if row["gender"] == "M":
        print(row)