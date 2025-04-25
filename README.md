# Latency Recorder 🚀

Latency Recorder, as its name suggests, is a tool to record the latency of remote servers or services over ping requests. It’s designed to be simple and light on resources 🪶, making it ideal for environments with limited resources.

## Features ✨

- Simple and easy to use ✅
- Low resource usage 💡
- Configurable ping interval per host ⏱️
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
- `latency_recorder`: The main application for recording server latency.
- `db`: A MariaDB database that stores the latency data.

## Usage ⚙️

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

## Contributing 🤝

We welcome contributions! Fork the repository and submit a pull request for bug fixes, new features, or documentation improvements. 🚀

Note: There are no GUIs or web interfaces at the moment. Interaction is done via the database. If you’d like a GUI or web interface, please open an issue and we’ll consider it for future updates.

## License 📜

This project is licensed under the GNU GPL v3 License. See the [LICENSE](LICENSE) file for details.
