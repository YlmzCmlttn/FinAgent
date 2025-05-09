from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv
from agents import Agent, Runner, gen_trace_id, trace, WebSearchTool
from agent_wrapper import send_message, initialize_agent_global
import asyncio
# Load environment variables

load_dotenv()

app = FastAPI(title="FinAgent Backend", description="Backend for OpenAI Agents")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # Initialize agent during application startup
    await initialize_agent_global()

class ChatRequest(BaseModel):
    message: str
    trace_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    trace_id: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Generate a new trace_id if not provided
        trace_id = request.trace_id or gen_trace_id()

        result = await send_message(request.message)

        response = result
        # Process the message with the agent
        print(f"Received message: {request.message}")
        print(f"Response: {response}")
        return ChatResponse(
            response=response,
            trace_id=trace_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():    
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 4000))
    uvicorn.run(app, host="0.0.0.0", port=port) 