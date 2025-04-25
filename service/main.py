from dotenv import load_dotenv
import os
import mariadb
import sys
from datetime import datetime
from rich.console import Console
from rich.table import Table
from ping3 import ping
import time

class remote_server:
    server_id: int
    server_name: str
    server_hostname: str
    test_interval: int
    test_max_retries: int
    test_timeout: int

    def __init__(self, server_id: int, server_name: str, server_hostname: str, test_interval: int, test_max_retries: int, test_timeout: int):
        self.server_id = server_id
        self.server_name = server_name
        self.server_hostname = server_hostname
        self.test_interval = test_interval
        self.test_max_retries = test_max_retries
        self.test_timeout = test_timeout

    def __str__(self):
        return f"Server ID: {self.server_id}, Name: {self.server_name}, Hostname: {self.server_hostname}, Interval: {self.test_interval}, Max Retries: {self.test_max_retries}, Timeout: {self.test_timeout}"


class latency_test:
    id: int
    server_id: int
    result: float
    success: bool
    created_at: str

    def __init__(self, id: int, server_id: int, result: float, success: bool, created_at: str):
        self.id = id
        self.server_id = server_id
        self.result = result
        self.success = success
        self.created_at = created_at

    def __str__(self):
        return f"Latency Test ID: {self.id}, Server ID: {self.server_id}, Result: {self.result}, Success: {self.success}, Created At: {self.created_at}"
    

load_dotenv()
conn = None

try:
    conn = mariadb.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    print("Connected to MariaDB successfully!")
except mariadb.Error as e:
    print(f"Error connecting to MariaDB: {e}")
    sys.exit(1)

g_cursor = conn.cursor()

def get_setting(name: str) -> str:
    """
    Get a setting from the database.
    :param key: The key of the setting to retrieve.
    :return: The value of the setting.
    """
    try:
        g_cursor.execute("SELECT value FROM settings WHERE name=?", (name,))
        result = g_cursor.fetchone()
        if result:
            return result[0]
        else:
            return None
    except mariadb.Error as e:
        print(f"Error retrieving setting {name}: {e}")
        return None

def set_setting(name: str, value: str) -> None:
    """
    Set a setting in the database.
    :param key: The key of the setting to set.
    :param value: The value of the setting.
    """
    try:
        g_cursor.execute("UPDATE settings SET value=? WHERE name=?", (value, name))
        conn.commit()
    except mariadb.Error as e:
        print(f"Error setting {name}: {e}")
        conn.rollback()

def close_connection() -> None:
    """
    Close the database connection.
    """
    if conn:
        conn.close()
        print("Connection closed.")
    else:
        print("No connection to close.")


if __name__ == "__main__":
    
    # Greeting message on startup - display current time
    console = Console()
    console.clear()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    console.print(f"[bold green]Service started at {current_time}[/bold green]")
    console.print(f"Welcome to {get_setting('app_name')} !")
    console.print()

    # Display :
    # 1. Author
    # 2. Version
    # 3. Description
    # 4. License
    app_author = get_setting("app_author")
    app_version = get_setting("app_version")
    app_description = get_setting("app_description")
    app_license = get_setting("app_license")
    console.print(f"[bold blue]Author:[/bold blue] {app_author}")
    console.print(f"[bold blue]Version:[/bold blue] {app_version}")
    console.print(f"[bold blue]Description:[/bold blue] {app_description}")
    console.print(f"[bold blue]License:[/bold blue] {app_license}")
    console.print()

    # List servers to be tested using a rich table
    g_cursor.execute("SELECT * FROM remote_servers WHERE test_active=1")
    servers = g_cursor.fetchall()

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", justify="right")
    table.add_column("Name", style="bold")
    table.add_column("Hostname")
    table.add_column("Interval")
    table.add_column("Max Retries")
    table.add_column("Timeout")

    for server in servers:
        server_obj = remote_server(server[0], server[1], server[2], server[3], server[4], server[5])
        table.add_row(str(server_obj.server_id), str(server_obj.server_name), str(server_obj.server_hostname), str(server_obj.test_interval), str(server_obj.test_max_retries), str(server_obj.test_timeout))

    # Last latency for each server. Select with join and limit 1
    g_cursor.execute("SELECT rs.id, rs.server_name, lt.result, lt.success, lt.created_at FROM remote_servers rs LEFT JOIN latency_tests lt ON rs.id = lt.server_id WHERE rs.test_active=1 AND lt.id = (SELECT MAX(id) FROM latency_tests WHERE server_id = rs.id)")
    latency_tests = g_cursor.fetchall()

    table2 = Table(show_header=True, header_style="bold magenta")
    table2.add_column("ID", justify="right")
    table2.add_column("Name", style="bold")
    table2.add_column("Last Latency")
    table2.add_column("Success")
    
    for latency_test in latency_tests:
        server_id = latency_test[0]
        server_name = latency_test[1]
        result = latency_test[2] if latency_test[2] is not None else "N/A"
        success = "Yes" if latency_test[3] else "No"
        created_at = latency_test[4] if latency_test[4] is not None else "N/A"
        table2.add_row(str(server_id), str(server_name), str(result), str(success), str(created_at))

    # Print the tables
    console.print("[bold blue]Servers to be tested:[/bold blue]")
    console.print(table)
    console.print("[bold blue]Last latency for each server:[/bold blue]")
    console.print(table2)

    # Run in the background. Execute the needed ping on each server if the interval is reached
    # Check if the interval is reached
    # If yes, run the ping command and store the result in the database
    # If no, wait for the next interval

    def run_latency_test(server_id: int, server_hostname: str, server_name: str, test_interval: int) -> None:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # get the most recent test time for the server
        g_cursor.execute("SELECT created_at FROM latency_tests WHERE server_id=? ORDER BY created_at DESC LIMIT 1", (server_id,))
        
        row = g_cursor.fetchone()
        run_test = False

        if row is None:
            run_test = True
        else:
            try:
                if isinstance(row[0], str):
                    last_test_time = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
                else:
                    last_test_time = row[0]
                elapsed_seconds = (datetime.now() - last_test_time).total_seconds()
                if elapsed_seconds >= test_interval:
                    run_test = True
            except Exception as e:
                console.print(f"[bold red]Error parsing last test time for {server_name}: {e}[/bold red]")

        if run_test:
            console.print(f"[bold yellow]Running test for {server_name} ({server_hostname})...[/bold yellow]")
            try:
                # Retrieve timeout (default to 5 seconds if not set or invalid)
                timeout_setting = get_setting("test_timeout")
                test_timeout = float(timeout_setting) if timeout_setting else 5.0
            except Exception:
                test_timeout = 5.0

            try:
                result = ping(server_hostname, timeout=test_timeout)
                if result is False or result is None:
                    success = False
                    avg_rtt = 0.0
                else:
                    success = True
                    avg_rtt = result * 1000  # converting seconds to milliseconds
            except Exception as e:
                console.print(f"[bold red]Ping error for {server_name}: {e}[/bold red]")
                success = False
                avg_rtt = 0.0

            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                g_cursor.execute(
                    "INSERT INTO latency_tests (server_id, result, success, created_at) VALUES (?, ?, ?, ?)",
                    (server_id, avg_rtt, success, created_at)
                )
                conn.commit()
                console.print(f"[bold green]Test for {server_name} completed. Result: {avg_rtt} ms[/bold green]")
            except mariadb.Error as e:
                console.print(f"[bold red]Database error for {server_name}: {e}[/bold red]")
                conn.rollback()
        else:
            console.print(f"[bold blue]Waiting for next interval for {server_name}...[/bold blue]")

    while True:
        # Retrieve all remote servers with their hostname, name, and test interval
        g_cursor.execute("SELECT id, server_hostname, server_name, test_interval FROM remote_servers WHERE test_active=1")
        servers = g_cursor.fetchall()

        for server in servers:
            server_id, server_hostname, server_name, test_interval = server
            run_latency_test(server_id, server_hostname, server_name, test_interval)

        time.sleep(5)
