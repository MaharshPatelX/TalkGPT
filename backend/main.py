from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import Dict, Any, List
from pydantic import BaseModel
from datetime import datetime
from contextlib import asynccontextmanager
import uvicorn
import uuid
import json

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage

from database import connect_database, get_database
from config import ALLOWED_ORIGINS, OPENAI_API_KEY, LANGCHAIN_MODEL, LANGCHAIN_TEMPERATURE, LANGCHAIN_MAX_TOKENS

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    connect_database()
    yield
    # Shutdown (if needed)

app = FastAPI(
    title="Claude Chat Application",
    description="Simple AI chat interface with LangChain ChatOpenAI",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize LangChain ChatOpenAI
chat_model = ChatOpenAI(
    model_name=LANGCHAIN_MODEL,
    temperature=LANGCHAIN_TEMPERATURE,
    max_tokens=LANGCHAIN_MAX_TOKENS,
    openai_api_key=OPENAI_API_KEY,
    streaming=True
)

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    session_id: str = None

class SessionCreate(BaseModel):
    session_id: str = None

class SessionUpdate(BaseModel):
    name: str


@app.get("/")
async def root():
    return {"message": "Claude Chat Application API"}

@app.post("/api/sessions/create")
async def create_session(session_data: SessionCreate = None):
    """Create a new session"""
    try:
        db = get_database()
        session_id = session_data.session_id if session_data and session_data.session_id else str(uuid.uuid4())
        
        session_doc = {
            "session_id": session_id,
            "name": f"Chat {session_id[:8]}",
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow()
        }
        
        db.sessions.insert_one(session_doc)
        return {"session_id": session_id, "created_at": session_doc["created_at"]}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

@app.post("/api/chat")
async def chat_completion(request: ChatRequest):
    """Generate chat completion"""
    try:
        if not request.session_id:
            request.session_id = str(uuid.uuid4())
        
        db = get_database()
        
        # Get conversation history
        messages = list(db.messages.find(
            {"session_id": request.session_id}
        ).sort("sequence_number", 1))
        
        # Convert to LangChain format
        langchain_messages = []
        for msg in messages:
            if msg["role"] == "user":
                langchain_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                langchain_messages.append(AIMessage(content=msg["content"]))
        
        # Add current user message
        langchain_messages.append(HumanMessage(content=request.message))
        
        # Generate response
        response = chat_model.invoke(langchain_messages)
        
        # Save user message
        user_msg_doc = {
            "session_id": request.session_id,
            "role": "user",
            "content": request.message,
            "sequence_number": len(messages) + 1,
            "created_at": datetime.utcnow()
        }
        db.messages.insert_one(user_msg_doc)
        
        # Save assistant message
        assistant_msg_doc = {
            "session_id": request.session_id,
            "role": "assistant",
            "content": response.content,
            "sequence_number": len(messages) + 2,
            "created_at": datetime.utcnow()
        }
        db.messages.insert_one(assistant_msg_doc)
        
        return {
            "response": response.content,
            "session_id": request.session_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat completion failed: {str(e)}")

@app.post("/api/chat/stream")
async def chat_completion_stream(request: ChatRequest):
    """Generate streaming chat completion"""
    try:
        if not request.session_id:
            request.session_id = str(uuid.uuid4())
        
        db = get_database()
        
        # Get conversation history
        messages = list(db.messages.find(
            {"session_id": request.session_id}
        ).sort("sequence_number", 1))
        
        # Convert to LangChain format
        langchain_messages = []
        for msg in messages:
            if msg["role"] == "user":
                langchain_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                langchain_messages.append(AIMessage(content=msg["content"]))
        
        # Add current user message
        langchain_messages.append(HumanMessage(content=request.message))
        
        # Save user message
        user_msg_doc = {
            "session_id": request.session_id,
            "role": "user",
            "content": request.message,
            "sequence_number": len(messages) + 1,
            "created_at": datetime.utcnow()
        }
        db.messages.insert_one(user_msg_doc)
        
        async def generate_stream():
            """Generate streaming response"""
            full_response = ""
            try:
                async for chunk in chat_model.astream(langchain_messages):
                    content = chunk.content
                    if content:
                        full_response += content
                        data = json.dumps({"content": content, "session_id": request.session_id})
                        yield f"data: {data}\n\n"
                
                # Save complete assistant response
                assistant_msg_doc = {
                    "session_id": request.session_id,
                    "role": "assistant",
                    "content": full_response,
                    "sequence_number": len(messages) + 2,
                    "created_at": datetime.utcnow()
                }
                db.messages.insert_one(assistant_msg_doc)
                
                # Send completion signal
                yield f"data: {json.dumps({'done': True, 'session_id': request.session_id})}\n\n"
                
            except Exception as e:
                error_data = json.dumps({"error": str(e)})
                yield f"data: {error_data}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Streaming failed: {str(e)}")

@app.get("/api/sessions/{session_id}/messages")
async def get_messages(session_id: str):
    """Get messages for a session"""
    try:
        db = get_database()
        messages = list(db.messages.find(
            {"session_id": session_id}
        ).sort("sequence_number", 1))
        
        # Convert ObjectId to string
        for msg in messages:
            msg["_id"] = str(msg["_id"])
        
        return {"messages": messages}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get messages: {str(e)}")

@app.get("/api/sessions")
async def get_sessions():
    """Get all sessions"""
    try:
        db = get_database()
        sessions = list(db.sessions.find().sort("last_activity", -1))
        
        # Convert ObjectId to string and add message count
        for session in sessions:
            session["_id"] = str(session["_id"])
            message_count = db.messages.count_documents({"session_id": session["session_id"]})
            session["message_count"] = message_count
        
        return {"sessions": sessions}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get sessions: {str(e)}")

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and all its messages"""
    try:
        db = get_database()
        
        # Check if session exists
        session = db.sessions.find_one({"session_id": session_id})
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Delete all messages for this session
        db.messages.delete_many({"session_id": session_id})
        
        # Delete the session
        result = db.sessions.delete_one({"session_id": session_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"message": "Session deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")

@app.put("/api/sessions/{session_id}")
async def update_session(session_id: str, session_update: SessionUpdate):
    """Update session name"""
    try:
        db = get_database()
        
        # Check if session exists
        session = db.sessions.find_one({"session_id": session_id})
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Update the session name
        result = db.sessions.update_one(
            {"session_id": session_id},
            {
                "$set": {
                    "name": session_update.name,
                    "last_activity": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"message": "Session updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update session: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)