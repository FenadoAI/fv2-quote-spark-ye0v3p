from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime

# AI agents
from ai_agents.agents import AgentConfig, SearchAgent, ChatAgent


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# AI agents init
agent_config = AgentConfig()
search_agent: Optional[SearchAgent] = None
chat_agent: Optional[ChatAgent] = None

# Main app
app = FastAPI(title="AI Agents API", description="Minimal AI Agents API with LangGraph and MCP support")

# API router
api_router = APIRouter(prefix="/api")


# Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str


# AI agent models
class ChatRequest(BaseModel):
    message: str
    agent_type: str = "chat"  # "chat" or "search"
    context: Optional[dict] = None


class ChatResponse(BaseModel):
    success: bool
    response: str
    agent_type: str
    capabilities: List[str]
    metadata: dict = Field(default_factory=dict)
    error: Optional[str] = None


class SearchRequest(BaseModel):
    query: str
    max_results: int = 5


class SearchResponse(BaseModel):
    success: bool
    query: str
    summary: str
    search_results: Optional[dict] = None
    sources_count: int
    error: Optional[str] = None


# Quote generation models
class QuoteRequest(BaseModel):
    theme: str
    custom_theme: Optional[str] = None


class QuoteResponse(BaseModel):
    success: bool
    quote: str
    author: str
    theme: str
    error: Optional[str] = None

# Routes
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]


# AI agent routes
@api_router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    # Chat with AI agent
    global search_agent, chat_agent
    
    try:
        # Init agents if needed
        if request.agent_type == "search" and search_agent is None:
            search_agent = SearchAgent(agent_config)
            
        elif request.agent_type == "chat" and chat_agent is None:
            chat_agent = ChatAgent(agent_config)
        
        # Select agent
        agent = search_agent if request.agent_type == "search" else chat_agent
        
        if agent is None:
            raise HTTPException(status_code=500, detail="Failed to initialize agent")
        
        # Execute agent
        response = await agent.execute(request.message)
        
        return ChatResponse(
            success=response.success,
            response=response.content,
            agent_type=request.agent_type,
            capabilities=agent.get_capabilities(),
            metadata=response.metadata,
            error=response.error
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return ChatResponse(
            success=False,
            response="",
            agent_type=request.agent_type,
            capabilities=[],
            error=str(e)
        )


@api_router.post("/search", response_model=SearchResponse)
async def search_and_summarize(request: SearchRequest):
    # Web search with AI summary
    global search_agent
    
    try:
        # Init search agent if needed
        if search_agent is None:
            search_agent = SearchAgent(agent_config)
        
        # Search with agent
        search_prompt = f"Search for information about: {request.query}. Provide a comprehensive summary with key findings."
        result = await search_agent.execute(search_prompt, use_tools=True)
        
        if result.success:
            return SearchResponse(
                success=True,
                query=request.query,
                summary=result.content,
                search_results=result.metadata,
                sources_count=result.metadata.get("tools_used", 0)
            )
        else:
            return SearchResponse(
                success=False,
                query=request.query,
                summary="",
                sources_count=0,
                error=result.error
            )
            
    except Exception as e:
        logger.error(f"Error in search endpoint: {e}")
        return SearchResponse(
            success=False,
            query=request.query,
            summary="",
            sources_count=0,
            error=str(e)
        )


@api_router.get("/agents/capabilities")
async def get_agent_capabilities():
    # Get agent capabilities
    try:
        capabilities = {
            "search_agent": SearchAgent(agent_config).get_capabilities(),
            "chat_agent": ChatAgent(agent_config).get_capabilities()
        }
        return {
            "success": True,
            "capabilities": capabilities
        }
    except Exception as e:
        logger.error(f"Error getting capabilities: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@api_router.post("/generate-quote", response_model=QuoteResponse)
async def generate_quote(request: QuoteRequest):
    """Generate a famous quote based on the provided theme"""
    global chat_agent

    try:
        # Initialize chat agent if needed
        if chat_agent is None:
            chat_agent = ChatAgent(agent_config)

        # Use custom theme if provided, otherwise use the selected theme
        theme = request.custom_theme if request.custom_theme else request.theme

        # Create a detailed prompt for generating authentic quotes
        quote_prompt = f"""Generate a famous, authentic quote about '{theme}'.

        Requirements:
        - The quote must be from a real, famous historical figure, author, philosopher, leader, or well-known personality
        - The quote should be relevant to the theme of '{theme}'
        - Return ONLY the quote text and author name in this exact format:
        Quote: "[quote text]"
        Author: [author name]

        Do not include any additional text, explanations, or formatting."""

        # Execute the agent
        result = await chat_agent.execute(quote_prompt)

        if result.success:
            # Parse the response to extract quote and author
            response_text = result.content.strip()

            # Extract quote and author using string parsing
            quote = ""
            author = ""

            lines = response_text.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('Quote:'):
                    quote = line.replace('Quote:', '').strip()
                    # Remove quotes if present
                    if quote.startswith('"') and quote.endswith('"'):
                        quote = quote[1:-1]
                elif line.startswith('Author:'):
                    author = line.replace('Author:', '').strip()

            # Fallback parsing if the format is different
            if not quote or not author:
                # Try to find quote in quotes and author after dash
                import re
                quote_match = re.search(r'"([^"]+)"', response_text)
                author_match = re.search(r'-\s*([^-\n]+)$', response_text, re.MULTILINE)

                if quote_match:
                    quote = quote_match.group(1)
                if author_match:
                    author = author_match.group(1).strip()

            # Final fallback - use the whole response as quote if parsing fails
            if not quote:
                quote = response_text
                author = "Unknown"

            return QuoteResponse(
                success=True,
                quote=quote,
                author=author,
                theme=theme
            )
        else:
            return QuoteResponse(
                success=False,
                quote="",
                author="",
                theme=theme,
                error=result.error
            )

    except Exception as e:
        logger.error(f"Error generating quote: {e}")
        return QuoteResponse(
            success=False,
            quote="",
            author="",
            theme=theme,
            error=str(e)
        )

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging config
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    # Initialize agents on startup
    global search_agent, chat_agent
    logger.info("Starting AI Agents API...")
    
    # Lazy agent init for faster startup
    logger.info("AI Agents API ready!")


@app.on_event("shutdown")
async def shutdown_db_client():
    # Cleanup on shutdown
    global search_agent, chat_agent
    
    # Close MCP
    if search_agent and search_agent.mcp_client:
        # MCP cleanup automatic
        pass
    
    client.close()
    logger.info("AI Agents API shutdown complete.")
