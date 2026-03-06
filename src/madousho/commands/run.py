"""Run command - Start the madousho service with flow loading."""
from pathlib import Path
from madousho.logger import logger
from madousho.flow.loader import load_plugin
from madousho.flow.registry import FlowRegistry

import typer


def run_cmd(ctx: typer.Context):
    """
    Start the madousho service.
    
    This command loads configuration, scans plugins/flows/ directory,
    validates and instantiates flow plugins, and registers them.
    """
    config_path = ctx.obj["config_path"]
    
    # Load configuration
    from madousho.config.loader import load_config
    config = load_config(str(config_path))
    
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
    
    logger.debug("Configuration loaded", extra={"config_path": str(config_path), "api_host": config.api.host, "api_port": config.api.port, "model_groups": list(config.model_groups.keys())})
