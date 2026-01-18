#!/usr/bin/env python3
"""
Main entry point for the Multi-Agent Research Analysis Platform.
"""

import sys
import uvicorn
from loguru import logger

from config import get_settings
from api import create_app

logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)


def main():
    logger.info("Starting Multi-Agent Research Analysis Platform")
    
    settings = get_settings()
    app = create_app()
    
    logger.info(f"Server will start on {settings.api_host}:{settings.api_port}")
    logger.info(f"Max agents: {settings.max_agents}")
    logger.info(f"Database: {settings.database_url}")
    logger.info(f"Vector DB: {settings.vector_db_type}")
    
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.log_level.lower(),
        access_log=True
    )


if __name__ == "__main__":
    main()
