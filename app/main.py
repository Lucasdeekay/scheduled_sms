from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from contextlib import asynccontextmanager

from app.database import engine, get_db, Base
from app.schemas import MessageCreate, MessageResponse
from app.crud import (
    create_message,
    get_all_messages,
    get_message_by_id
)
from app.scheduler import start_scheduler

# Create database tables
Base.metadata.create_all(bind=engine)

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start the scheduler
    scheduler = start_scheduler()
    yield
    # Shutdown: Stop the scheduler
    scheduler.shutdown()

# Initialize FastAPI app
app = FastAPI(
    title="Scheduled Messaging API",
    description="API for scheduling SMS messages via Twilio",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware (adjust origins for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# SECTION 11: API ENDPOINTS
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    """Welcome endpoint"""
    return {
        "message": "Scheduled Messaging API",
        "status": "active",
        "endpoints": {
            "create_message": "/messages/",
            "list_messages": "/messages/",
            "get_message": "/messages/{id}"
        }
    }

@app.post(
    "/messages/",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Messages"]
)
async def create_scheduled_message(
    message: MessageCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new scheduled message.
    
    - **sender_name**: Name of the person sending the message
    - **receiver_name**: Name of the recipient
    - **receiver_phone**: Phone number in format +1234567890
    - **message**: The message content (max 1600 chars)
    - **scheduled_time**: When to send (ISO format, must be future)
    """
    try:
        db_message = create_message(db, message)
        return db_message
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create message: {str(e)}"
        )

@app.get(
    "/messages/",
    response_model=List[MessageResponse],
    tags=["Messages"]
)
async def list_messages(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all scheduled messages with pagination.
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100)
    """
    messages = get_all_messages(db, skip=skip, limit=limit)
    return messages

@app.get(
    "/messages/{message_id}",
    response_model=MessageResponse,
    tags=["Messages"]
)
async def get_message(
    message_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific message by ID.
    
    - **message_id**: The ID of the message to retrieve
    """
    message = get_message_by_id(db, message_id)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Message with ID {message_id} not found"
        )
    return message

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "scheduled-messaging-api"}