## Dashboard

A simple FastAPI-based dashboard is included for monitoring bot activity and settings.

### Features

- View total messages per chat
- See recent messages (optionally filtered by chat)
- List all chats
- View settings per chat

### Running the Dashboard

The dashboard runs as a separate service in Docker Compose.

To start the dashboard (along with the bot):

```bash
make docker-up
```

The dashboard will be available at [http://localhost:8000](http://localhost:8000).

### API Endpoints

| Endpoint                  | Description                                 |
|---------------------------|---------------------------------------------|
| `/`                       | List available endpoints                    |
| `/messages/count`         | Get message count per chat                  |
| `/messages/recent`        | Get recent messages (optionally by chat)    |
| `/chats`                  | List all chat IDs                           |
| `/settings/{chat_id}`     | Get settings for a specific chat            |

You can also explore and test the API interactively at [http://localhost:8000/docs](http://localhost:8000/docs).

### Example: Query Recent Messages for a Chat

```
GET /messages/recent?chat_id=123456
```

---

```## Dashboard

A simple FastAPI-based dashboard is included for monitoring bot activity and settings.

### Features

- View total messages per chat
- See recent messages (optionally filtered by chat)
- List all chats
- View settings per chat

### Running the Dashboard

The dashboard runs as a separate service in Docker Compose.

To start the dashboard (along with the bot):

```bash
make docker-up
```

The dashboard will be available at [http://localhost:8000](http://localhost:8000).

### API Endpoints

| Endpoint                  | Description                                 |
|---------------------------|---------------------------------------------|
| `/`                       | List available endpoints                    |
| `/messages/count`         | Get message count per chat                  |
| `/messages/recent`        | Get recent messages (optionally by chat)    |
| `/chats`                  | List all chat IDs                           |
| `/settings/{chat_id}`     | Get settings for a specific chat            |

You can also explore and test the API interactively at [http://localhost:8000/docs](http://localhost:8000/docs).

### Example: Query Recent Messages for a Chat

```
GET /messages/recent?chat_id=123456