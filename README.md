# Blog Application

A modern blog application built with FastAPI and Vue.js, featuring a clean and responsive design.

## Features

- 🚀 Modern tech stack: FastAPI (Backend) + Vue 3 (Frontend)
- 🎨 Beautiful UI with Ant Design Vue
- 🔐 JWT-based authentication
- 📝 Full CRUD operations for articles
- 🎯 RESTful API design
- 🔍 Article search and filtering
- 📱 Responsive design for all devices

## Tech Stack

### Backend
- FastAPI - High-performance web framework
- SQLAlchemy - SQL toolkit and ORM
- PyMySQL - MySQL database adapter
- Python-Jose - JWT token handling
- Passlib - Password hashing
- Redis - Caching
- Uvicorn - ASGI server

### Frontend
- Vue 3 - Progressive JavaScript framework
- TypeScript - Type-safe JavaScript
- Ant Design Vue - UI component library
- Vue Router - Official router for Vue.js
- Vite - Next generation frontend tooling

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 16+
- MySQL 8.0+
- Redis 6.0+

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your database credentials and other settings
```

5. Run the server:
```bash
uvicorn app.main:app --reload
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

## API Documentation

Once the backend server is running, you can access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Features in Development

- [ ] Comment system
- [ ] Article categories and tags
- [ ] Advanced search functionality
- [ ] User profile management
- [ ] Image upload and management
- [ ] Article analytics

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.