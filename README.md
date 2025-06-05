# Latency Recorder 🚀

Latency Recorder, as its name suggests, is a tool to record the latency of remote servers or services over ping requests. It’s designed to be simple and light on resources 🪶, making it ideal for environments with limited resources.

## Features ✨

- Simple and easy to use ✅
- Low resource usage 💡
- Configurable ping interval per host ⏱️
- Configurable speed test timeout for remote files ⏳
- Change settings on the fly 🔄
- Database-first approach 🗄️

## Requirements 📋

- Docker 🐳
- Docker Compose 🔗
- Basic SQL and database management skills 🛠️

## Installation 🔧

1. Clone the repository 📥

2. Build and start the containers by running:
```bash
docker-compose up -d
```
This starts the following containers:
- `latency_recorder`: The main application for recording server latency and performing speed tests.
- `db`: A MariaDB database that stores the latency and speed test data.

## Usage ⚙️

### Latency Tests
1. Connect to the database with your preferred SQL client. By default, the database is exposed on port 3306, and the database name is `latency_recorder`. The default credentials are:
    - Username: `user`
    - Password: `password`
    
    You can adjust these in the `compose.yml` file under the `db` service.

2. Add your hosts to the `remote_servers` table in the database. The table has the following columns:
    - `id`: Auto-incremented host ID 🔢
    - `server_name`: The name of the host (e.g. `Google`) 🌐
    - `server_hostname`: The hostname or IP address (e.g. `google.com`) 📡
    - `interval`: Seconds between ping requests (e.g. `60` for one minute) ⏲️
    - `test_max_retries`: Maximum ping retries (e.g. `3`) 🔄
    - `test_timeout`: Ping timeout in seconds (e.g. `5`) ⏳
    - `test_active`: Enable (1) or disable (0) the host 🔘

3. View the results with the `latency_summary` view in the database:
```sql
SELECT * FROM latency_summary;
```

### Speed Tests for Remote Files
1. Add your remote files to the `remote_files` table in the database. The table has the following columns:
    - `id`: Auto-incremented file ID 🔢
    - `file_name`: The name of the file (e.g. `Large CSV Dataset`) 📂
    - `file_url`: The URL of the file to test (e.g. `https://example.com/large-dataset.csv`) 🌐
    - `test_interval`: Seconds between speed tests (e.g. `300` for every 5 minutes) ⏲️
    - `test_timeout`: Timeout for the speed test in seconds (e.g. `10`) ⏳
    - `test_active`: Enable (1) or disable (0) the file 🔘

2. View the results with the `speed_summary` view in the database:
```sql
SELECT * FROM speed_summary;
```

## Contributing 🤝

We welcome contributions! Fork the repository and submit a pull request for bug fixes, new features, or documentation improvements. 🚀

Note: There are no GUIs or web interfaces at the moment. Interaction is done via the database. If you’d like a GUI or web interface, please open an issue and we’ll consider it for future updates.

## License 📜

This project is licensed under the GNU GPL v3 License. See the [LICENSE](LICENSE) file for details.