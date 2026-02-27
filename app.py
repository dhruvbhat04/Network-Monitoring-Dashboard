from flask import Flask, render_template, request, redirect
import sqlite3
import subprocess

app = Flask(__name__)

# Create database table
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS devices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    ip TEXT
                )''')
    conn.commit()
    conn.close()

init_db()

# Ping function
def ping_device(ip):
    try:
        output = subprocess.check_output(
            ["ping", "-n", "1", ip],
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )

        if "TTL=" in output:
            latency = output.split("time=")[-1].split("ms")[0]
            return "Online", latency + " ms"
        else:
            return "Offline", "N/A"
    except:
        return "Offline", "N/A"

@app.route("/")
def index():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM devices")
    devices = c.fetchall()

    device_status = []

    for device in devices:
        status, latency = ping_device(device[2])
        device_status.append((device[1], device[2], status, latency))

    conn.close()
    return render_template("index.html", devices=device_status)

@app.route("/add", methods=["POST"])
def add_device():
    name = request.form["name"]
    ip = request.form["ip"]

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("INSERT INTO devices (name, ip) VALUES (?, ?)", (name, ip))
    conn.commit()
    conn.close()

    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)