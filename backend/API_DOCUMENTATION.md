# 📚 BookSmart AI – FastAPI Backend Documentation

## 🚀 Quick Start

### **Base URLs**
- **API base**: `http://localhost:8000`
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

### **Default Admin**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

Authenticate once, then include the JWT in `Authorization: Bearer <token>` for all protected routes.

---

## 🔐 Authentication (`/auth`)

All admin access is multi‑tenant: each `AdminUser` belongs to a `Salon`.

### **Register admin + salon**
```http
POST /auth/register
Content-Type: application/json

{
  "username": "owner1",
  "password": "strong-password",
  "salon_name": "My First Salon"
}
```

**Response**
```json
{
  "access_token": "jwt...",
  "token_type": "bearer",
  "salon_id": 1,
  "username": "owner1"
}
```

### **Login**
```http
POST /auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

### **Get current user**
```http
GET /auth/me
Authorization: Bearer <token>
```

---

## 💈 Services (`/services`)

Services belong to a salon (via `salon_id` on the model). The current implementation does not yet enforce tenant scoping – if you need strict multi‑tenant isolation, filter by `salon_id` at the DB layer.

### **List services**
```http
GET /services/
Authorization: Bearer <token>
```

### **Create service**
```http
POST /services/
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Haircut",
  "duration_minutes": 30,
  "price": 500,
  "description": "Standard haircut"
}
```

### **Get / delete service**
```http
GET    /services/{service_id}
DELETE /services/{service_id}
Authorization: Bearer <token>
```

---

## 👥 Staff (`/staff`)

Staff are linked to salons and are used to power analytics and (optionally) booking assignment.

Key routes (high‑level):
- `GET /staff/` – list staff
- `GET /staff/count` – staff statistics
- `POST /staff/` – add staff
- `PUT /staff/{id}` – update
- `DELETE /staff/{id}` – remove
- `POST /staff/batch-update` – batch add/remove for simulations or quick setup

Example – add staff:
```bash
curl -X POST http://localhost:8000/staff/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "working_hours": "9:00 AM - 6:00 PM"
  }'
```

---

## 📅 Bookings (`/bookings`)

Bookings are central to the system. Conflict detection and notifications are handled in `routers/bookings.py`.

### **Create booking (with conflict checks)**

```http
POST /bookings/
Authorization: Bearer <token>
Content-Type: application/json

{
  "customer_name": "John Doe",
  "customer_phone": "+91 98765 43210",
  "customer_email": "john@example.com",
  "service_id": 1,
  "staff_id": null,
  "appointment_time": "2026-04-07T10:00:00"
}
```

**Conflict behaviour**
- Before creating, `_check_conflicts` computes the time window based on `service.duration_minutes`.
- If any existing **confirmed** booking overlaps, the API returns:
```json
{
  "detail": "Time slot conflict: an existing booking (#X) for Alice overlaps with this time. Please choose a different time."
}
```
with **409** status.

### **List & inspect bookings**
```http
GET /bookings/
GET /bookings/{booking_id}
Authorization: Bearer <token>
```

### **Cancel booking**
```http
PATCH /bookings/{booking_id}/cancel
Authorization: Bearer <token>
```

Effects:
- Status set to `"cancelled"`.
- Real‑time event broadcast on WebSocket channel (if realtime service is running).

### **Reschedule booking**
```http
PATCH /bookings/{booking_id}/reschedule
Authorization: Bearer <token>
Content-Type: application/json

{
  "appointment_time": "2026-04-08T15:00:00"
}
```

Validation:
- Time must be in the future.
- Conflict detection is re‑run; if slot is taken, 409 is returned.

---

## 💬 AI Chat & Booking (`/chat`)

The chat router powers the **AI receptionist** and booking automation.

### **Chat endpoint**
```http
POST /chat/
Content-Type: application/json

{
  "salon_id": "1",
  "message": "Hi, I want to book a haircut tomorrow at 5 PM."
}
```

Pipeline (simplified):
1. `handle_chat` parses `salon_id` and inspects `message`.
2. If it detects **booking intent** (`book`, `appointment`, `schedule`, etc.), it:
   - Extracts service name from DB services.
   - Parses date/time (`YYYY-MM-DD HH:MM`), name (`name is ...`), phone, email.
   - Checks for conflicts.
   - Creates a real `Booking` record if everything is valid.
3. Otherwise it calls `llm_chain.execute_chat`, which:
   - Pulls salon context from the local FAISS index (`rag_pipeline.py`).
   - Uses Gemini to generate a salon‑aware response (if quota allows).
   - Falls back to a deterministic local reply if LLM fails (e.g. quota exceeded).

**Example booking message**:
```text
Book Haircut on 2026-04-11 17:00, name is Rahul Verma, phone +919876543211
```

**Typical success response**:
```json
{
  "answer": "Done. Your booking is confirmed (ID #3) for Haircut on 11 Apr 2026 at 05:00 PM."
}
```

### **RAG ingestion**

```http
POST /chat/ingest/{salon_id}
Authorization: Bearer <token>
```

This:
- Fetches services and staff for the salon.
- Builds/updates a FAISS vector index under `./vector_indexes/{salon_id}`.
- Allows Gemini responses to reference salon‑specific services, prices, and policies.

---

## ⭐ Reviews (`/reviews`)

The reviews router attaches a single `Review` to each `Booking`.

Key routes:
- `GET /reviews/{salon_id}` – list reviews for a salon.
- `POST /reviews/` – submit a review for a completed booking.

Example submit:
```bash
curl -X POST http://localhost:8000/reviews/ \
  -H "Content-Type: application/json" \
  -d '{
    "booking_id": 1,
    "service_id": 1,
    "salon_id": 1,
    "customer_name": "John Doe",
    "rating": 5,
    "comment": "Great experience!"
  }'
```

---

## 📊 Analytics (`/analytics/{salon_id}`)

Provides dashboard analytics for a given `salon_id`:
- Total bookings, confirmed/cancelled counts.
- Total revenue.
- Staff count.
- Top services by bookings and revenue.

```http
GET /analytics/{salon_id}
Authorization: Bearer <token>
```

Used directly by the admin dashboard UI.

---

## 💰 Payments (`/payments`)

Razorpay integration is used for online payments after a booking is created.

Main routes:
- `POST /payments/create-order` – create a Razorpay order for a booking.
- `POST /payments/verify` – verify payment signature and mark booking as paid.

Razorpay keys are read from:
```bash
RAZORPAY_KEY_ID=...
RAZORPAY_KEY_SECRET=...
```

---

## 🔔 Reminders (`/reminders`)

Automated reminders are scheduled via APScheduler on app startup (`main.py`).

- `POST /reminders/trigger` – manually trigger a scan for upcoming bookings and dispatch SMS/Email reminders.

Startup hook:
- `@app.on_event("startup")` seeds a default demo salon and starts the reminder scheduler.

---

## 🌐 Realtime (`/realtime`)

Realtime router provides WebSocket events for dashboard updates.

When bookings are created or cancelled, `broadcast_sync` in `routers/realtime.py` pushes events to connected dashboards.

Example events:
- `"new_booking"` – broadcast when a booking is created.
- `"booking_cancelled"` – broadcast when cancelled.

---

## 🎤 Voice (`/voice`)

Voice endpoints integrate with Twilio and STT/TTS providers to run the AI receptionist on phone calls.

Key ideas:
- Webhooks for incoming calls from Twilio.
- Uses the same booking and AI chat logic underneath.

---

## 🔧 Environment & Deployment

### **Environment variables (.env)**

```bash
# Database
DATABASE_URL=sqlite:///./booksmart.db  # default; use PostgreSQL in production

# Twilio SMS & Voice
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1234567890

# AI / LLM
GEMINI_API_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key   # optional

# Voice STT/TTS
DEEPGRAM_API_KEY=...
GOOGLE_TTS_API_KEY=...

# JWT
JWT_SECRET_KEY=super-secret

# Razorpay
RAZORPAY_KEY_ID=...
RAZORPAY_KEY_SECRET=...
```

### **Docker (example)**

```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONUNBUFFERED=1
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🧪 Quick cURL Recipes

### Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### Create booking (no conflict)
```bash
TOKEN=ey...
curl -X POST http://localhost:8000/bookings/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "John Doe",
    "customer_phone": "+91 98765 43210",
    "customer_email": "john@example.com",
    "service_id": 1,
    "staff_id": null,
    "appointment_time": "2026-04-07T10:00:00"
  }'
```

### AI chat booking
```bash
curl -X POST http://localhost:8000/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "salon_id": "1",
    "message": "Book Haircut on 2026-04-11 17:00, name is Rahul Verma, phone +919876543211"
  }'
```

---

## 📞 Support Notes

- Use `http://localhost:8000/docs` during development for live, interactive docs.
- Check server logs to debug Twilio, Razorpay, and Gemini issues (especially quota errors).
- Default admin (`admin` / `admin123`) is intended only for local development; change credentials and `JWT_SECRET_KEY` for production.

