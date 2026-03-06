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
    verbose = ctx.obj["verbose"]
    
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
                
                # Log warnings (always show config validation warnings)
                if result.warnings:
                    for warning in result.warnings:
                        logger.warning(f"  Warning: {warning}")
                else:
                    logger.error(f"✗ Failed to load flow plugin {plugin_path.name}")
                    for error in result.errors:
                        logger.error(f"  Error: {error}")
                        
            except Exception as e:
                logger.error(f"✗ Error loading flow plugin {plugin_path.name}: {e}")
                if verbose:
                    import traceback
                    logger.debug(traceback.format_exc())
    else:
        logger.info(f"No plugins/flows directory found")
    
    # Report registered flows
    registry = FlowRegistry.get_instance()
    registered_flows = registry.list_all()
    if registered_flows:
        logger.info(f"Registered flows: {', '.join(registered_flows)}")
    else:
        logger.info("No flows registered")
    
    if verbose:
        logger.info("Configuration loaded", config_path=str(config_path), api_host=config.api.host, api_port=config.api.port, model_groups=list(config.model_groups.keys()))
