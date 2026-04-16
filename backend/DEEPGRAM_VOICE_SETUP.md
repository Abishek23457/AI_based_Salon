# 🎙️ Deepgram Voice Agent Setup Guide

Complete guide for setting up real-time voice chat with BookSmart AI using Deepgram.

## 📚 Deepgram Documentation References

- **Getting Started**: https://developers.deepgram.com/docs/getting-started-with-pre-recorded-audio
- **Live Streaming (STT)**: https://developers.deepgram.com/docs/getting-started-with-live-streaming-audio
- **Text-to-Speech**: https://developers.deepgram.com/docs/tts-getting-started
- **Python SDK**: https://github.com/deepgram/deepgram-python-sdk
- **API Console**: https://console.deepgram.com/

---

## 🚀 Quick Start (3 Steps)

### Step 1: Get Deepgram API Key
1. Go to https://console.deepgram.com/signup
2. Create a free account (no credit card required)
3. Copy your API key from the dashboard

### Step 2: Add to .env
```bash
# Add this line to your .env file
DEEPGRAM_API_KEY=your_deepgram_api_key_here
```

### Step 3: Run Setup
```bash
# Option A: Double-click this file
setup_deepgram.bat

# Option B: Or run in terminal
cd c:\Users\abish\OneDrive\Desktop\aa\booksmart\backend
py setup_deepgram.bat
```

---

## 🎯 Usage

### Voice Chat (Full Conversation)
```bash
# Double-click OR run in terminal:
deepgram_voice_chat.bat
```

**How it works:**
1. Press ENTER when ready to speak
2. Speak into your microphone
3. AI transcribes your speech → processes → responds with voice
4. Press ENTER again to continue or Ctrl+C to exit

### Test TTS Only
```bash
py deepgram_voice_chat.py --test-tts
```

---

## 📦 Files Created

| File | Purpose |
|------|---------|
| `deepgram_voice_service.py` | Core Deepgram service (STT/TTS) |
| `deepgram_voice_chat.py` | Terminal voice chat interface |
| `deepgram_voice_chat.bat` | One-click launcher |
| `setup_deepgram.bat` | Setup & dependency installer |
| `DEEPGRAM_VOICE_SETUP.md` | This documentation |

---

## 🔧 Architecture

```
User Microphone → Deepgram STT (WebSocket) → Text → AI Processing → 
Deepgram TTS → Audio → User Speakers
```

**Components:**
- **STT**: Deepgram Nova-2 model (16kHz, WebSocket streaming)
- **TTS**: Deepgram Aura voices (Asteria, Luna, etc.)
- **Audio**: PyAudio for mic input & speaker output

---

## 📝 API Details

### Deepgram STT (Live Streaming)
```python
WebSocket URL: wss://api.deepgram.com/v1/listen
Parameters:
  - encoding=linear16 (16-bit PCM)
  - sample_rate=16000 (16kHz)
  - language=en-IN (Indian English)
  - model=nova-2 (latest model)
  - smart_format=true (punctuation)
```

### Deepgram TTS
```python
HTTP URL: https://api.deepgram.com/v1/speak
Models:
  - aura-asteria-en (default, warm female)
  - aura-luna-en (professional female)
  - aura-orion-en (male)
  - aura-stella-en (energetic female)
```

---

## 🎛️ Configuration

### Voice Settings (deepgram_voice_service.py)
```python
# TTS Voice Options
voice = "aura-asteria-en"  # Warm, friendly
voice = "aura-luna-en"     # Professional
voice = "aura-orion-en"    # Male voice

# Audio Settings
RATE = 16000       # Sample rate (16kHz)
CHANNELS = 1     # Mono
CHUNK = 1024      # Buffer size
```

### AI Persona (deepgram_voice_chat.py)
```python
SYSTEM_PROMPT = """You are BookSmart AI, a friendly salon receptionist..."""
```

---

## 🧪 Testing

### 1. Test Audio Devices
```bash
py -c "import pyaudio; p = pyaudio.PyAudio(); print('Devices:', p.get_device_count()); p.terminate()"
```

### 2. Test TTS Only
```bash
py deepgram_voice_chat.py --test-tts
```

### 3. Test Service Module
```bash
py deepgram_voice_service.py
```

---

## ❗ Troubleshooting

### Issue: "DEEPGRAM_API_KEY not found"
**Solution:**
```bash
# Check .env file
type .env | findstr DEEPGRAM

# Add if missing
echo DEEPGRAM_API_KEY=your_key >> .env
```

### Issue: "No microphone found"
**Solution:**
1. Check Windows Sound Settings
2. Ensure mic is enabled and not muted
3. Set as default recording device
4. Test with: `py -c "import pyaudio; p = pyaudio.PyAudio(); print([p.get_device_info_by_index(i)['name'] for i in range(p.get_device_count()) if p.get_device_info_by_index(i)['maxInputChannels'] > 0])"`

### Issue: PyAudio installation fails
**Solution:**
```bash
# Windows: Download pre-built wheel
# 1. Go to: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
# 2. Download PyAudio‑0.2.11‑cp311‑cp311‑win_amd64.whl (match your Python version)
# 3. Install:
py -m pip install PyAudio‑0.2.11‑cp311‑cp311‑win_amd64.whl
```

### Issue: "WebSocket connection failed"
**Solution:**
1. Check internet connection
2. Verify API key is valid at https://console.deepgram.com/
3. Check firewall isn't blocking wss:// connections

---

## 💰 Pricing

**Deepgram Free Tier:**
- $200 credit for 45 days
- Then: Pay-as-you-go
- STT: ~$0.0043/minute
- TTS: ~$0.0025/1K characters

**Perfect for:**
- Development & testing
- Small salons (< 100 calls/day)

---

## 🔐 Security

- API key stored in `.env` (never commit to git)
- HTTPS/WSS connections only
- No audio data stored (real-time streaming)

---

## 📊 Comparison: Deepgram vs Other Options

| Feature | Deepgram | Google TTS | Azure Speech |
|---------|----------|------------|----------------|
| Real-time STT | ✅ Yes | ✅ Yes | ✅ Yes |
| Indian English | ✅ Excellent | ⚠️ Good | ⚠️ Good |
| Latency | ~300ms | ~500ms | ~400ms |
| Pricing | 💰 Free tier | 💰💰 Paid | 💰💰 Paid |
| Setup | ⭐ Easy | ⚠️ Complex | ⚠️ Complex |
| Offline | ❌ No | ❌ No | ❌ No |

**Winner for BookSmart AI:** Deepgram 🎉

---

## 🎉 Next Steps

1. ✅ Get API key: https://console.deepgram.com/signup
2. ✅ Add to .env: `DEEPGRAM_API_KEY=your_key`
3. ✅ Run setup: `setup_deepgram.bat`
4. ✅ Start chatting: `deepgram_voice_chat.bat`

---

## 📞 Support

**Deepgram:**
- Docs: https://developers.deepgram.com/
- Discord: https://discord.gg/deepgram
- Email: support@deepgram.com

**BookSmart AI:**
- Check logs in terminal
- Review `deepgram_voice_service.py`
- Test with `py deepgram_voice_chat.py --test-tts`

---

**Ready to speak with AI?** 🎙️ Run `deepgram_voice_chat.bat` now!
