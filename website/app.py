from flask import Flask, render_template
import mariadb
import os

app = Flask(__name__)

def get_db_connection():
    return mariadb.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

@app.route("/")
def index():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch latency summary
        cursor.execute("SELECT server_name, ROUND(average_latency, 2), ROUND(max_latency, 2), ROUND(min_latency, 2), ROUND(average_latency_15min, 2), ROUND(average_latency_30min, 2), ROUND(average_latency_24h, 2), ROUND(fail_rate, 2), test_count FROM latency_summary")
        latency_results = cursor.fetchall()

        # Fetch speed summary
        cursor.execute("SELECT file_name, average_speed, max_speed, min_speed, average_speed_15min, average_speed_30min, average_speed_24h, test_count FROM speed_summary")
        speed_results = cursor.fetchall()
        
        print("Latency Results:", latency_results)
        print("Speed Results:", speed_results)
        
        # Check the result of the last latency test
        cursor.execute("SELECT success FROM latency_tests ORDER BY id DESC LIMIT 1")
        last_latency_test = cursor.fetchone()
        last_test_failed = last_latency_test and last_latency_test[0] == 0

        if last_test_failed:
            print("Last latency test failed.")
        else:
            print("Last latency test succeeded.")

        conn.close()
        return render_template(
            "index.html",
            latency_results=latency_results,
            speed_results=speed_results,
            last_test_failed=last_test_failed
        )
    except mariadb.Error as e:
        return f"Database error: {e}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)