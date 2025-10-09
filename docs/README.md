# Door FastAPI Application

A modern Python web application built with FastAPI for managing stocks, information, and notes.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   Create a `.env` file with your database configuration (see main README for details)

3. **Run the application:**
   ```bash
   python main.py
   ```
   
   **Note:** When starting the local dev site, the database automatically syncs with Neon (production) using smart-sync mode:
   - First pulls new records from Neon → Local (preserves production additions)
   - Then pushes all records from Local → Neon (ensures complete sync)
   - This happens before the server starts and only runs in local development mode

4. **Access the application:**
   - Web interface: http://localhost:8000
   - API documentation: http://localhost:8000/docs
   - Alternative API docs: http://localhost:8000/redoc

## Features

- **Modern UI**: Clean, responsive interface with Bootstrap 5
- **Stock Management**: Track investments and transactions
- **Information Management**: Store URLs with automatic source detection
- **Notes Management**: Organize personal notes with categories
- **REST API**: Full API endpoints for all functionality
- **PostgreSQL Integration**: Robust database backend

## API Endpoints

- `GET /` - Home page
- `GET /stocks/` - Stock management interface
- `GET /information/` - Information management interface
- `GET /notes/` - Notes management interface
- `GET /api/docs` - Interactive API documentation

## Development

```bash
# Run with auto-reload
uvicorn main:app --reload

# Run with specific host/port
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Testing

```bash
pytest
```

For more detailed information, see the main README.md file.
