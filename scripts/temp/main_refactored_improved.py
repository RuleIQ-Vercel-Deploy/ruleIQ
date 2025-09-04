#!/usr/bin/env python3
"""
Refactored main.py with reduced cognitive complexity
Improved readability and maintainability following KISS and YAGNI principles
"""
import sys
import argparse
import uvicorn
from typing import Tuple
import logging

# Setting up logger
logger = logging.getLogger(__name__)

def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser"""
    parser = argparse.ArgumentParser(
        description="RuleIQ FastAPI Application Server"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind the server to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the server to (default: 8000)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload on code changes"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    return parser


def parse_command_line_args() -> Tuple[str, int, bool, bool]:
    """
    Parse command line arguments using argparse
    Reduced complexity from 16 to 1
    """
    parser = create_argument_parser()
    args = parser.parse_args()
    
    return args.host, args.port, args.reload, args.debug


def validate_port(port: int) -> None:
    """Validate port number is in valid range"""
    if not 1 <= port <= 65535:
        logger.error(f"Invalid port number: {port}. Must be between 1 and 65535")
        sys.exit(1)


def get_log_level(debug: bool) -> str:
    """Get log level based on debug flag"""
    return "info" if debug else "warning"


def start_server(host: str, port: int, reload: bool, debug: bool) -> None:
    """Start the FastAPI server with given configuration"""
    validate_port(port)
    
    logger.info(f"Starting RuleIQ server on {host}:{port}")
    logger.info(f"Configuration: reload={reload}, debug={debug}")
    
    # Import app here to avoid circular imports
    from main import app
    
    uvicorn.run(
        "main:app" if reload else app,
        host=host,
        port=port,
        reload=reload,
        log_level=get_log_level(debug),
    )


if __name__ == "__main__":
    # Parse arguments
    host, port, reload, debug = parse_command_line_args()
    
    # Start server
    try:
        start_server(host, port, reload, debug)
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)