# BookSmart AI - Intelligent Salon Management System

A comprehensive AI-powered salon management platform with voice AI, chat automation, payment integration, and advanced analytics.

## 🚀 Live Demo

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

## 📋 Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Backend Architecture](#backend-architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)

## ✨ Features

### Core Features
- **🔐 Authentication** - JWT-based secure login system
- **📅 Booking Management** - Create, update, cancel appointments
- **👥 Customer Management** - Customer profiles and history
- **💇 Staff Management** - Staff scheduling and performance tracking
- **🛎️ Services Catalog** - Service listings with pricing

### AI-Powered Features
- **🤖 AI Chat Assistant** - 24/7 customer support with RAG
- **🗣️ Voice AI** - Speech-to-speech conversation
- **📱 Texting AI** - Natural conversation flow understanding
- **🧠 Smart Recommendations** - Personalized service suggestions
- **🔮 Demand Forecasting** - AI-powered booking predictions

### Communication
- **📞 Phone Integration** - Exotel voice call handling
- **💬 WhatsApp Business** - Booking confirmations & reminders
- **📧 Email Templates** - Rich HTML email notifications
- **🔔 Push Notifications** - Web push for real-time updates
- **📲 SMS Service** - Text message notifications

### Business Features
- **💳 Razorpay Payments** - Complete payment processing
- **🎁 Gift Cards** - Digital gift card system
- **⭐ Loyalty Program** - Points and rewards system
- **⏰ Waitlist** - Automated slot notifications
- **🔄 Recurring Bookings** - Weekly/monthly appointments
- **⭐ Reviews** - Customer rating and feedback system

### Analytics & Security
- **📊 Analytics Dashboard** - Revenue, staff, customer insights
- **📈 Advanced Reporting** - Business intelligence
- **🛡️ Audit Logs** - Complete activity tracking
- **🔑 RBAC** - Role-based access control
- **🌍 Multi-language** - Hindi, Tamil, Telugu, and more

## 🛠️ Technology Stack

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| React | 19.2.4 | UI Framework |
| Vite | 5.2.8 | Build Tool |
| TypeScript | 5.x | Type Safety |
| Tailwind CSS | 3.4.19 | Styling |
| React Router | 6.22.3 | Navigation |
| Framer Motion | 12.38.0 | Animations |
| Lucide React | 1.7.0 | Icons |

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.12 | Language |
| FastAPI | 0.115 | Web Framework |
| Uvicorn | ASGI Server | HTTP Server |
| SQLAlchemy | 2.x | ORM |
| SQLite/PostgreSQL | - | Database |
| Deepgram | - | Speech-to-Text |
| OpenRouter | - | AI/LLM |
| Razorpay | - | Payments |
| Exotel | - | Voice/SMS |

## 📁 Project Structure

```
booksmart/
├── backend/                    # FastAPI Backend
│   ├── routers/               # API Route Handlers
│   │   ├── auth.py           # Authentication
│   │   ├── bookings.py       # Booking CRUD
│   │   ├── services.py       # Services management
│   │   ├── staff.py          # Staff management
│   │   ├── chat.py           # AI chat endpoints
│   │   ├── analytics.py      # Basic analytics
│   │   ├── payments.py       # Payment processing
│   │   ├── reviews.py        # Reviews system
│   │   ├── reminders.py      # Automated reminders
│   │   ├── whatsapp.py       # WhatsApp integration
│   │   ├── giftcards.py      # Gift cards
│   │   ├── loyalty.py        # Loyalty program
│   │   ├── waitlist.py       # Waitlist management
│   │   ├── recurring.py      # Recurring bookings
│   │   ├── reviewsapi.py     # Reviews API
│   │   ├── advanced_analytics.py # Advanced analytics
│   │   └── ...
│   ├── services/             # Service Layer
│   │   └── notifications.py  # Push notifications
│   ├── main.py              # Application entry
│   ├── models.py            # Database models
│   ├── schemas.py           # Pydantic schemas
│   ├── config.py            # Configuration
│   ├── database.py          # DB connection
│   ├── auth_utils.py        # JWT utilities
│   ├── rag_pipeline.py      # RAG for AI
│   ├── llm_chain.py         # LLM integration
│   ├── intelligent_ai.py    # AI chat logic
│   ├── texting_ai.py        # Texting AI
│   ├── voice_chat_agent.py  # Voice bot
│   ├── razorpay_integration.py # Payments
│   ├── whatsapp_client.py   # WhatsApp
│   ├── exotel_client.py     # Exotel API
│   ├── email_client.py      # Email service
│   ├── email_templates.py   # Email templates
│   ├── gift_cards.py        # Gift cards
│   ├── loyalty_program.py   # Loyalty system
│   ├── waitlist_service.py  # Waitlist
│   ├── recurring_bookings.py # Recurring
│   ├── review_system.py     # Reviews
│   ├── analytics_dashboard.py # Analytics
│   ├── ai_recommendations.py # AI recommendations
│   ├── i18n_service.py      # Multi-language
│   ├── audit_logger.py      # Audit logs
│   ├── rbac_service.py      # Access control
│   └── ...
├── frontend/                 # React Frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   │   ├── Navbar.tsx
│   │   │   ├── Footer.tsx
│   │   │   ├── Hero.tsx
│   │   │   ├── Features.tsx
│   │   │   ├── ServicesGrid.tsx
│   │   │   ├── BookingForm.tsx
│   │   │   ├── ChatWidget.tsx
│   │   │   ├── Testimonials.tsx
│   │   │   ├── Pricing.tsx
│   │   │   ├── StaffManagement.tsx
│   │   │   └── dashboard/   # Dashboard components
│   │   ├── pages/          # Page components
│   │   │   ├── HomePage.tsx
│   │   │   └── DashboardPage.tsx
│   │   ├── App.tsx         # Main app component
│   │   ├── main.tsx        # Entry point
│   │   └── globals.css     # Global styles
│   ├── index.html          # HTML template
│   ├── vite.config.ts      # Vite config
│   ├── tailwind.config.ts  # Tailwind config
│   └── package.json        # Dependencies
├── README.md               # This file
├── docker-compose.yml      # Docker setup
└── requirements.txt        # Python deps

```

## 🏗️ Backend Architecture

### Core Modules

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| **main.py** | Application entry | FastAPI app, router registration |
| **models.py** | Database models | SQLAlchemy ORM definitions |
| **schemas.py** | Data validation | Pydantic request/response models |
| **config.py** | Configuration | Environment variables, settings |
| **database.py** | DB connection | Session management |

### AI & Voice

| Module | Purpose | Features |
|--------|---------|----------|
| **intelligent_ai.py** | Smart chat AI | Intent recognition, context awareness |
| **texting_ai.py** | Text conversation | Natural texting patterns |
| **voice_chat_agent.py** | Voice bot | STT/TTS, real-time audio |
| **llm_chain.py** | LLM integration | OpenRouter/Gemini API |
| **rag_pipeline.py** | Knowledge base | Vector search, embeddings |
| **ai_recommendations.py** | Smart recommendations | Personalized suggestions |

### Communication

| Module | Purpose | Integration |
|--------|---------|-------------|
| **whatsapp_client.py** | WhatsApp messaging | WhatsApp Business API |
| **exotel_client.py** | Voice/SMS | Exotel API |
| **email_client.py** | Email service | SMTP integration |
| **email_templates.py** | Rich emails | HTML templates |

### Business Logic

| Module | Purpose | Features |
|--------|---------|----------|
| **razorpay_integration.py** | Payments | Orders, refunds, webhooks |
| **gift_cards.py** | Gift cards | Purchase, redeem, balance |
| **loyalty_program.py** | Loyalty | Points, tiers, rewards |
| **waitlist_service.py** | Waitlist | Slot notifications |
| **recurring_bookings.py** | Recurring | Weekly/monthly bookings |
| **review_system.py** | Reviews | Ratings, moderation |
| **analytics_dashboard.py** | Analytics | Revenue, performance |
| **audit_logger.py** | Audit | Activity tracking |
| **rbac_service.py** | Security | Role-based access |
| **i18n_service.py** | Localization | Multi-language support |

### API Routers

| Router | Endpoint | Features |
|--------|----------|----------|
| **auth** | /auth/* | Login, register, JWT |
| **bookings** | /bookings/* | CRUD operations |
| **services** | /services/* | Service management |
| **staff** | /staff/* | Staff management |
| **chat** | /chat/* | AI chat endpoints |
| **payments** | /payments/* | Razorpay integration |
| **whatsapp** | /api/whatsapp/* | WhatsApp messaging |
| **giftcards** | /api/gift-cards/* | Gift card management |
| **loyalty** | /api/loyalty/* | Loyalty program |
| **waitlist** | /api/waitlist/* | Waitlist management |
| **recurring** | /api/recurring/* | Recurring bookings |
| **reviewsapi** | /api/reviews-system/* | Reviews |
| **analytics** | /api/analytics/* | Advanced analytics |
| **exotel** | /exotel/* | Voice calls |

## 📦 Installation

### Prerequisites
- Python 3.12+
- Node.js 18+
- npm or yarn
- Git

### Clone Repository
```bash
git clone https://github.com/Abishek23457/proj1.git
cd proj1/booksmart
```

### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy .env.example .env
```

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Or with yarn
yarn install
```

## ⚙️ Configuration

### Backend Environment Variables (.env)
```env
# Database
DATABASE_URL=sqlite:///./booksmart.db

# JWT Secret
SECRET_KEY=your-secret-key-here

# AI APIs
DEEPGRAM_API_KEY=your-deepgram-key
OPENROUTER_API_KEY=your-openrouter-key
GEMINI_API_KEY=your-gemini-key

# Communication
EXOTEL_SID=your-exotel-sid
EXOTEL_TOKEN=your-exotel-token
WHATSAPP_API_KEY=your-whatsapp-key
RAZORPAY_KEY_ID=your-razorpay-key
RAZORPAY_KEY_SECRET=your-razorpay-secret

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email
SMTP_PASS=your-password
```

### Frontend Configuration
The frontend uses environment variables from `.env`:
```env
VITE_API_URL=http://localhost:8000
```

## 🚀 Running the Application

### Method 1: Manual Start

**Terminal 1 - Backend:**
```bash
cd backend
py -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Method 2: Docker Compose
```bash
docker-compose up -d
```

### Access Points
- **Website:** http://localhost:3000
- **API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Admin:** Login at /login

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /auth/login | User login |
| POST | /auth/register | User registration |

### Bookings
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /bookings/ | List bookings |
| POST | /bookings/ | Create booking |
| GET | /bookings/{id} | Get booking |
| PUT | /bookings/{id} | Update booking |
| DELETE | /bookings/{id} | Cancel booking |

### Services
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /services/ | List services |
| POST | /services/ | Create service |
| PUT | /services/{id} | Update service |

### Staff
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /staff/ | List staff |
| POST | /staff/ | Add staff |
| PUT | /staff/{id} | Update staff |

### Payments (Razorpay)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /payments/create-order | Create order |
| POST | /payments/verify | Verify payment |
| POST | /payments/refund | Process refund |
| GET | /payments/stats | Payment stats |

### AI Chat
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /chat | Basic chat |
| POST | /intelligent-chat | Smart AI chat |
| POST | /texting-chat | Texting AI |
| POST | /chat-agent/chat | Chat agent |

## 🧪 Testing

### Run Backend Tests
```bash
cd backend
pytest
```

### Run Razorpay Test
```bash
cd backend
py test_razorpay.py
```

### API Testing with curl
```bash
# Health check
curl http://localhost:8000/health

# Create booking
curl -X POST http://localhost:8000/bookings/ \
  -H "Content-Type: application/json" \
  -d '{"customer_name":"Test","service_id":1,"staff_id":1,"date":"2026-04-20","time":"10:00"}'
```

## 🚢 Deployment

### Docker Deployment
```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f
```

### Production Checklist
- [ ] Set production environment variables
- [ ] Configure HTTPS/SSL
- [ ] Set up PostgreSQL database
- [ ] Configure Redis for caching
- [ ] Set up monitoring/logging
- [ ] Configure backup strategy
- [ ] Test all payment flows
- [ ] Verify email delivery

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License.

## 👨‍💻 Author

**Abishek** - [GitHub](https://github.com/Abishek23457)

## 🙏 Acknowledgments

- Deepgram for voice AI
- OpenRouter for LLM access
- Razorpay for payment processing
- Exotel for telephony
- FastAPI team for the amazing framework
- React team for the frontend library

---

## 📞 Support

For support, email support@booksmart.ai or join our Slack channel.

**Happy Coding! 🎉**
