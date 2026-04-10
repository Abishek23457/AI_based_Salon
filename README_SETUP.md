# BookSmart AI - Clean Setup

## FastAPI Backend + React Frontend

### Backend Setup (FastAPI)

1. **Install Python Dependencies:**
```bash
cd backend
pip install fastapi uvicorn pydantic python-dotenv
```

2. **Start the Backend Server:**
```bash
python app.py
```

3. **Access Swagger UI Documentation:**
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **API Status**: http://localhost:8000/

### Frontend Setup (React)

1. **Install Node.js Dependencies:**
```bash
cd react-frontend
npm install
```

2. **Start the React App:**
```bash
npm start
```

3. **Access the Frontend:**
- **React App**: http://localhost:3000

### Features

#### Backend (FastAPI)
- **Swagger Documentation**: Complete API docs at `/docs`
- **AI Chat Endpoint**: `/texting-chat`
- **Authentication**: `/auth/login`
- **API Status**: `/api/status`
- **CORS Enabled**: For React frontend

#### Frontend (React)
- **Modern UI**: Clean, responsive design
- **AI Chat Widget**: Working chat interface
- **Navigation**: Professional navbar
- **Features Section**: Service highlights
- **Real-time Chat**: Connects to backend API

### Test the System

1. Start both servers (backend on 8000, frontend on 3000)
2. Open http://localhost:3000 in browser
3. Click the chat button (bottom right)
4. Type a message and test the AI response
5. Visit http://localhost:8000/docs for API documentation

### Default Login
- **Username**: admin
- **Password**: admin123

### API Endpoints

- `GET /` - API Root
- `POST /auth/login` - User authentication
- `POST /texting-chat` - AI chat endpoint
- `GET /api/status` - System status

This setup provides a clean, working FastAPI backend with React frontend without any errors.
