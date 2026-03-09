import subprocess
import json
import sqlite3
import datetime
import time

SPEED_TEST_EXECUTABLE_PATH=r"C:\Users\del\Desktop\cs50 projects\speedtest.exe"
# Save results to SQLite database continuously
conn = sqlite3.connect('speed_results.db')
TEST_INTERVAL_SECONDS = 60  # Run the test every 60 seconds
while True:
    st = subprocess.run([SPEED_TEST_EXECUTABLE_PATH, "--accept-license", "--accept-gdpr", "-f", "json"], capture_output=True, text=True)
    if st.returncode != 0:
        print("Error running speedtest:", st.stderr)
        exit(1) 
        
    # Find the best server based on ping
    results = json.loads(st.stdout)
    best_server = results["server"]

    # Perform the download and upload tests
    download_mbps = results["download"]["bandwidth"]*8 / 1_000_000
    upload_mbps = results["upload"]["bandwidth"]*8 / 1_000_000
    ping_ms = results["ping"]["latency"]

    print(f"Download: {download_mbps:.2f} Mbps")
    print(f"Upload:   {upload_mbps:.2f} Mbps")
    print(f"Ping:     {ping_ms:.0f} ms")

    download_MB_per_second = download_mbps / 8
    print(f"Download: {download_MB_per_second:.2f} MB/s")
    upload_MB_per_second = upload_mbps / 8
    print(f"Upload:   {upload_MB_per_second:.2f} MB/s")

    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS results
                (timestamp TEXT, download REAL, upload REAL, ping REAL)''')
    timestamp = datetime.datetime.now().isoformat()
    c.execute("INSERT INTO results VALUES (?, ?, ?, ?)",
            (timestamp, download_mbps, upload_mbps, ping_ms))
    conn.commit()
    print(f"Results saved to database at {timestamp}")
    print(f"Waiting for {TEST_INTERVAL_SECONDS} seconds before the next test...")
    time.sleep(TEST_INTERVAL_SECONDS)
conn.close()    