# Ngrok Configuration for BookSmart AI

## Setup Instructions

### 1. Install Ngrok
```bash
# Download ngrok from https://ngrok.com/download
# Or use chocolatey: choco install ngrok
# Or use npm: npm install -g ngrok
```

### 2. Backend Ngrok (FastAPI - Port 8000)
```bash
ngrok http 8000
```

### 3. Frontend Ngrok (Next.js - Port 3000)
```bash
ngrok http 3000
```

## Configuration Files

### Ngrok Config (ngrok.yml)
```yaml
version: "2"
authtoken: YOUR_NGROK_AUTH_TOKEN

tunnels:
  backend:
    proto: http
    addr: 8000
    host_header: localhost:8000
    bind_tls: true
    inspect: false
    web_addr: 4040
    
  frontend:
    proto: http
    addr: 3000
    host_header: localhost:3000
    bind_tls: true
    inspect: false
    web_addr: 4041
```

## Usage

### Start Both Tunnels
```bash
# Backend tunnel
ngrok start backend --config ngrok.yml

# Frontend tunnel (in separate terminal)
ngrok start frontend --config ngrok.yml
```

### Or Start Individually
```bash
# Backend only
ngrok http 8000

# Frontend only  
ngrok http 3000
```

## Access URLs

After starting ngrok, you'll get public URLs like:
- **Backend**: https://random-string.ngrok.io/docs (Swagger UI)
- **Frontend**: https://random-string.ngrok.io (React App)

## Environment Updates

### Update Frontend API URLs
When using ngrok, update your frontend API calls to use the ngrok URL:

```javascript
// In your React components
const API_BASE_URL = 'https://your-backend-ngrok-url.ngrok.io';

// Example fetch call
fetch(`${API_BASE_URL}/texting-chat`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message, customer_name: 'Customer' })
})
```

### Update CORS in Backend
Make sure your FastAPI backend allows the ngrok URL:

```python
# In app.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-frontend-ngrok-url.ngrok.io"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Advanced Configuration

### Custom Subdomains (Paid Plan)
```yaml
tunnels:
  backend:
    proto: http
    addr: 8000
    subdomain: booksmart-backend
    hostname: booksmart-backend.ngrok.io
```

### Static Domains (Paid Plan)
```yaml
tunnels:
  backend:
    proto: http
    addr: 8000
    domain: api.booksmart.ai
```

## Security Notes

1. **Auth Token**: Always set up an auth token
2. **HTTPS**: Ngrok provides HTTPS automatically
3. **Access Control**: Use ngrok's whitelist/blacklist features
4. **Rate Limiting**: Implement rate limiting on your APIs
5. **Environment Variables**: Don't expose sensitive data

## Troubleshooting

### Common Issues
- **Port Already in Use**: Stop other services using ports 3000/8000
- **CORS Errors**: Update CORS settings in backend
- **Connection Refused**: Check if servers are running locally
- **Ngrok Limit**: Free tier has limitations, consider upgrading

### Debug Commands
```bash
# Check ngrok status
ngrok diagnose

# List active tunnels
ngrok list

# Stop all tunnels
ngrok kill
```

## Monitoring

### Ngrok Web Interface
- **Backend**: http://localhost:4040
- **Frontend**: http://localhost:4041 (if using different web_addr)

### View Logs
```bash
# Real-time logs
ngrok http 8000 --log=stdout

# Log to file
ngrok http 8000 --log=ngrok.log
```

## Production Considerations

For production, consider:
1. **Paid Ngrok Plan**: For custom domains and more features
2. **Domain Setup**: Configure custom domains
3. **SSL Certificates**: Ngrok handles SSL automatically
4. **Load Balancing**: For high-traffic applications
5. **Monitoring**: Set up proper monitoring and alerting
