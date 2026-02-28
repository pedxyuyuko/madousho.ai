"""Show-config command - Display the current configuration."""

import typer
import yaml


def show_config_cmd(ctx: typer.Context):
    """
    Display the current configuration in YAML format.
    
    Loads the configuration and outputs it as YAML to stdout.
    Useful for debugging and verifying configuration.
    """
    config_path = ctx.obj["config_path"]
    
    from madousho.config.loader import load_config
    config = load_config(str(config_path))
    
    # Convert Config to dict and output as YAML
    config_dict = config.model_dump()
    yaml_output = yaml.dump(config_dict, default_flow_style=False, sort_keys=False)
    typer.echo(yaml_output)
