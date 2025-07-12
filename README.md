# TalkGPT

A modern AI chat application built with **Next.js**, **FastAPI**, and **LangChain ChatOpenAI**. Features unique URLs for each chat session and a ChatGPT-inspired interface.

## Features

- 🤖 **LangChain ChatOpenAI Integration** - Direct connection to OpenAI's GPT models
- 🔗 **Unique Chat URLs** - Each chat session has a shareable, persistent URL
- 🎨 **ChatGPT-Inspired UI** - Modern dark theme with clean, minimal design
- 💬 **Markdown Support** - Rich text formatting with syntax highlighting
- 📱 **Responsive Design** - Optimized for desktop and mobile
- 🗂️ **Chat Management** - Create, rename, and delete chat sessions
- 💾 **Persistent Storage** - Conversations saved in MongoDB
- 🏠 **Clean Homepage** - Centered input box for starting new conversations
- 🚀 **No Authentication** - Start chatting immediately

## Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **MongoDB** (running locally)
- **OpenAI API Key**

## Quick Start

### 1. Install MongoDB

Make sure MongoDB is running locally on `mongodb://localhost:27017`

**macOS (with Homebrew):**
```bash
brew install mongodb-community
brew services start mongodb-community
```

**Ubuntu/Debian:**
```bash
sudo apt install mongodb
sudo systemctl start mongodb
```

**Windows:**
Download and install from [MongoDB official site](https://www.mongodb.com/try/download/community)

### 2. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Add your OpenAI API key to .env file
echo "OPENAI_API_KEY=your_actual_api_key_here" > .env

# Start the backend server
python main.py
```

Backend will be running at: `http://localhost:8000`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the frontend
npm run dev
```

Frontend will be running at: `http://localhost:3000`

## Usage

### Starting a New Chat
1. **Open your browser** and go to `http://localhost:3000`
2. **Type your message** in the centered input box
3. **Press Enter** - A new chat session is created automatically
4. **Get a unique URL** - You'll be redirected to `/chat/[session-id]`

### Managing Chats
- **Sidebar Navigation** - View all your chat sessions
- **Rename Chats** - Hover over a chat and click the edit icon
- **Delete Chats** - Hover over a chat and click the trash icon
- **New Chat** - Click "New chat" button or the home icon to start fresh
- **Share Chats** - Copy the unique URL to share specific conversations

### Interface Features
- **Homepage** - Clean, centered input for new conversations
- **Chat Area** - Messages with markdown formatting and code syntax highlighting
- **Responsive Design** - Works on desktop and mobile devices

## API Endpoints

### Chat
- `POST /api/chat` - Send a message and get response
- `POST /api/chat/stream` - Send a message and get streaming response

### Sessions
- `POST /api/sessions/create` - Create a new session
- `GET /api/sessions` - Get all sessions
- `GET /api/sessions/{session_id}/messages` - Get messages for a session
- `DELETE /api/sessions/{session_id}` - Delete a session and its messages
- `PUT /api/sessions/{session_id}` - Update session name

## Project Structure

```
TalkGPT/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main application with API endpoints
│   ├── config.py           # Configuration settings
│   ├── database.py         # MongoDB connection
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Environment variables
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # Next.js 14 app router
│   │   │   ├── page.tsx          # Homepage with centered input
│   │   │   ├── chat/[sessionId]/ # Dynamic chat routes
│   │   │   └── layout.tsx        # Root layout
│   │   └── components/    # React components
│   │       ├── HomeInterface.tsx    # Homepage component
│   │       ├── ChatInterface.tsx    # Main chat interface
│   │       ├── ChatArea.tsx         # Chat messages area
│   │       └── Sidebar.tsx          # Chat sessions sidebar
│   ├── package.json       # Node dependencies
│   └── tailwind.config.js # Styling configuration
└── README.md              # This file
```

## Configuration

### Backend Configuration (`backend/config.py`)

```python
# Database
MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "talkgpt"

# LangChain Settings
LANGCHAIN_MODEL = "gpt-3.5-turbo"        # or "gpt-4"
LANGCHAIN_TEMPERATURE = 0.7               # 0.0 to 1.0
LANGCHAIN_MAX_TOKENS = 1000              # Max response length
```

### Environment Variables (`backend/.env`)

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

## Database Collections

The application creates these MongoDB collections automatically:

- **sessions** - Chat sessions with metadata (id, name, timestamps)
- **messages** - Chat messages with conversation history and sequence numbers

## Troubleshooting

### MongoDB Connection Issues
```bash
# Check if MongoDB is running
mongosh

# If connection fails, start MongoDB
brew services start mongodb-community  # macOS
sudo systemctl start mongodb          # Linux
```

### OpenAI API Issues
- Make sure your API key is correct in `backend/.env`
- Check your OpenAI account has sufficient credits
- Verify the model name in `config.py` (e.g., "gpt-3.5-turbo")

### Port Issues
- Backend runs on port 8000
- Frontend runs on port 3000
- Make sure these ports are available

## Development

### Adding New Models
Edit `backend/config.py`:
```python
LANGCHAIN_MODEL = "gpt-4"  # or any supported OpenAI model
```

### Changing Response Style
Edit `backend/config.py`:
```python
LANGCHAIN_TEMPERATURE = 0.9  # More creative (0.0 = focused, 1.0 = creative)
LANGCHAIN_MAX_TOKENS = 2000  # Longer responses
```

## License

MIT License - feel free to use this for your own projects!

## Key Features Implementation

### URL Routing
- **Homepage**: `/` - Clean interface for starting new chats
- **Chat Sessions**: `/chat/[sessionId]` - Unique URLs for each conversation
- **Auto-redirect**: New chats automatically redirect to unique URLs

### UI/UX Design
- **Dark Theme**: Custom color scheme (#181818, #212121, #303030)
- **Responsive Layout**: Sidebar with chat history and main chat area
- **Markdown Rendering**: Code blocks with syntax highlighting and copy buttons
- **Message Alignment**: User messages on right, AI responses on left

### Chat Management
- **Session Persistence**: Each chat gets a unique ID and URL
- **Rename/Delete**: Hover-based actions for chat management
- **Navigation**: Seamless routing between different chat sessions

## Contributing

Feel free to fork and modify this project! Some areas for enhancement:
- Add user authentication
- Implement chat sharing/collaboration
- Add more AI model options
- Enhance mobile responsiveness
- Add chat search functionality