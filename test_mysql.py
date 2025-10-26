import os
import mysql.connector
from mysql.connector import Error

print("=== 🔍 Checking MySQL Environment Variables ===")
env_vars = ["MYSQLHOST", "MYSQLPORT", "MYSQLUSER", "MYSQLPASSWORD", "MYSQLDATABASE"]
for var in env_vars:
    print(f"{var} = {os.getenv(var)}")

print("\n=== 🚀 Testing MySQL Connection ===")

db_config = {
    "host": os.getenv("MYSQLHOST"),
    "user": os.getenv("MYSQLUSER"),
    "password": os.getenv("MYSQLPASSWORD"),
    "database": os.getenv("MYSQLDATABASE"),
    "port": int(os.getenv("MYSQLPORT", 3306)),
}

try:
    print(f"Attempting connection to host: {db_config['host']}:{db_config['port']} ...")
    conn = mysql.connector.connect(**db_config)
    if conn.is_connected():
        print("✅ SUCCESS: Connected to MySQL database!")
        cursor = conn.cursor()
        cursor.execute("SELECT DATABASE();")
        record = cursor.fetchone()
        print("Current database:", record)
        cursor.close()
        conn.close()
except Error as e:
    print("❌ FAILED TO CONNECT!")
    print("Error details:", e)
    print("\n💡 Possible causes:")
    print(" - MYSQLHOST may be internal (use lev.proxy.rlwy.net or IP instead).")
    print(" - GitHub Actions cannot resolve IPv6 hostname.")
    print(" - Port may be closed or misconfigured.")
    print(" - Password or database name may be incorrect.")
