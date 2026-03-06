"""Run command - Start the madousho service with flow loading."""
import signal
import sys
from pathlib import Path
from typing import Optional

from madousho.logger import logger
from madousho.flow.loader import load_plugin
from madousho.flow.registry import FlowRegistry
from madousho.config.loader import get_config
import typer


def _start_api_server(config) -> None:
    """
    Start the FastAPI server with uvicorn.
    
    Handles:
    - Port conflicts (OSError)
    - Graceful shutdown on SIGTERM/SIGINT
    """
    import socket
    import uvicorn
    from madousho.api.app import create_app
    
    host = config.api.host
    port = config.api.port
    
    # Check if port is already in use before starting
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
            s.bind((host, port))
    except OSError as e:
        logger.error(f"")
        logger.error(f"ERROR: Port {port} is already in use.")
        logger.error(f"Please use a different port or stop the process using it.")
        logger.error(f"")
        raise typer.Exit(code=1) from e
    
    logger.info(f"Starting API server on {host}:{port}")
    
    # Create the FastAPI app
    app = create_app()
    
    def handle_signal(signum: int, frame: object) -> None:
        """Handle SIGTERM and SIGINT for graceful shutdown."""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        sys.exit(0)
    
    # Register signal handlers
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)
    
    try:
        uvicorn.run(app, host=host, port=port, log_level="info")
    except OSError as e:
        if "Address already in use" in str(e) or "address already in use" in str(e).lower():
            logger.error(f"")
            logger.error(f"ERROR: Port {port} is already in use.")
            logger.error(f"Please use a different port or stop the process using it.")
            logger.error(f"")
            raise typer.Exit(code=1)
        raise


def _start_api_server(config) -> None:
    """
    Start the FastAPI server with uvicorn.
    
    Handles:
    - Port conflicts (OSError)
    - Graceful shutdown on SIGTERM/SIGINT
    """
    import socket
    import uvicorn
    from madousho.api.app import create_app
    
    host = config.api.host
    port = config.api.port
    
    # Check if port is already in use before starting
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
            s.bind((host, port))
    except OSError as e:
        logger.error(f"")
        logger.error(f"ERROR: Port {port} is already in use.")
        logger.error(f"Please use a different port or stop the process using it.")
        logger.error(f"")
        raise typer.Exit(code=1) from e
    
    logger.info(f"Starting API server on {host}:{port}")
    
    # Create the FastAPI app
    app = create_app()
    
    def handle_signal(signum: int, frame: object) -> None:
        """Handle SIGTERM and SIGINT for graceful shutdown."""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        sys.exit(0)
    
    # Register signal handlers
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)
    
    try:
        uvicorn.run(app, host=host, port=port, log_level="info")
    except OSError as e:
        if "Address already in use" in str(e) or "address already in use" in str(e).lower():
            logger.error(f"")
            logger.error(f"ERROR: Port {port} is already in use.")
            logger.error(f"Please use a different port or stop the process using it.")
            logger.error(f"")
            raise typer.Exit(code=1)
        raise

def serve_cmd(ctx: typer.Context):
    """
    Start the madousho service.
    
    This command loads configuration, scans plugins/flows/ directory,
    validates and instantiates flow plugins, and registers them.
    """
    config = get_config()
    
    logger.info("Starting madousho service...")
    
    # Load flow plugins from plugins/flows/ directory
    plugins_dir = Path("plugins/flows")
    if plugins_dir.exists():
        logger.info(f"Loading flow plugins from {plugins_dir}")
        registry = FlowRegistry.get_instance()
        global_config_dict = config.model_dump()
        
        for plugin_path in plugins_dir.iterdir():
            # Skip non-directories and hidden directories
            if not plugin_path.is_dir() or plugin_path.name.startswith("."):
                continue
            
            logger.info(f"Loading flow plugin: {plugin_path.name}")
            
            try:
                result = load_plugin(plugin_path, global_config_dict)
                
                if result.success and result.plugin:
                    flow_name = result.plugin.metadata.name
                    if result.plugin.flow_instance:
                        registry.register(flow_name, result.plugin.flow_instance)
                    logger.info(f"✓ Flow plugin loaded: {flow_name}")
                
                # Log warnings (config validation issues)
                if result.warnings:
                    plugin_logger = logger.bind(plugin=f"[{result.plugin.metadata.name}] ") if result.success and result.plugin else logger
                    for warning in result.warnings:
                        plugin_logger.warning(f"Config: {warning}")
                else:
                    logger.error(f"✗ Failed to load flow plugin {plugin_path.name}")
                    for error in result.errors:
                        logger.error(f"Config: {error}")
                        
            except Exception as e:
                logger.error(f"✗ Error loading flow plugin {plugin_path.name}: {e}")
                logger.debug("Stacktrace:", exc_info=True)
    else:
        logger.info(f"No plugins/flows directory found")
    
    # Report registered flows
    registry = FlowRegistry.get_instance()
    registered_flows = registry.list_all()
    if registered_flows:
        logger.info(f"Registered flows: {', '.join(registered_flows)}")
    else:
        logger.info("No flows registered")
    
    # Start API server
    _start_api_server(config)
