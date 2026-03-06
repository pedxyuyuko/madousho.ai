"""Flow plugin configuration loader with typehint validation."""

import importlib.util
import sys
# Compatibility import: tomllib is 3.11+, tomli is backport for 3.10
try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Python 3.10 fallback
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from ..config.typehint_models import TypeHintDefinition, TypeHintValidator
from .base import FlowBase
from .models import FlowPlugin, FlowPluginConfig, FlowPluginMetadata, PluginLoadResult

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from ..config.typehint_models import TypeHintDefinition, TypeHintValidator
from .models import FlowPluginConfig


def normalize_keys(obj: Any) -> Any:
    """Recursively convert hyphenated keys to underscores."""
    if isinstance(obj, dict):
        return {k.replace('-', '_'): normalize_keys(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [normalize_keys(item) for item in obj]
    else:
        return obj



def load_flow_config(plugin_path: Path) -> FlowPluginConfig:
    """
    Load flow plugin's config.yaml.
    
    Args:
        plugin_path: Path to the flow plugin root directory
        
    Returns:
        FlowPluginConfig object
        
    Raises:
        FileNotFoundError: If config.yaml does not exist
        ValueError: If config.yaml is invalid YAML or fails validation
    """
    config_file = plugin_path / "config.yaml"
    
    if not config_file.exists():
        raise FileNotFoundError(f"Flow config file not found: {config_file}")
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            content = yaml.safe_load(f)
            config_data = content if content is not None else {}
            # Normalize keys (convert hyphens to underscores)
            config_data = normalize_keys(config_data)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in {config_file}: {e}")
    
    try:
        return FlowPluginConfig.model_validate(config_data)
    except Exception as e:
        raise ValueError(f"Invalid flow config: {e}")


def load_typehint(plugin_path: Path) -> Optional[TypeHintDefinition]:
    """
    Load flow plugin's config.typehint.yaml (optional).
    
    Args:
        plugin_path: Path to the flow plugin root directory
        
    Returns:
        TypeHintDefinition if config.typehint.yaml exists, None otherwise
        
    Raises:
        ValueError: If config.typehint.yaml is invalid YAML or fails validation
    """
    typehint_file = plugin_path / "config.typehint.yaml"
    
    if not typehint_file.exists():
        return None
    
    try:
        with open(typehint_file, 'r', encoding='utf-8') as f:
            content = yaml.safe_load(f)
            typehint_data = content if content is not None else {}
            # Normalize keys (convert hyphens to underscores)
            typehint_data = normalize_keys(typehint_data)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in {typehint_file}: {e}")
    
    try:
        return TypeHintDefinition.model_validate(typehint_data)
    except Exception as e:
        raise ValueError(f"Invalid typehint definition: {e}")


def validate_flow_config(
    plugin_path: Path,
    global_config: Dict[str, Any]
) -> Tuple[bool, FlowPluginConfig, List[str], List[str]]:
    """
    Validate flow plugin configuration against its typehint definition.
    
    Args:
        plugin_path: Path to the flow plugin root directory
        global_config: Global madousho configuration (for MODEL_GROUP validation)
        
    Returns:
        Tuple of (is_valid, config, errors, warnings)
        - is_valid: True if validation passed
        - config: Loaded FlowPluginConfig
        - errors: List of error messages
        - warnings: List of warning messages
    """
    errors: List[str] = []
    warnings: List[str] = []
    
    # Step 1: Load flow config.yaml
    try:
        config = load_flow_config(plugin_path)
    except FileNotFoundError as e:
        errors.append(str(e))
        return False, FlowPluginConfig(), errors, warnings
    except ValueError as e:
        errors.append(str(e))
        return False, FlowPluginConfig(), errors, warnings
    
    # Step 2: Load optional config.typehint.yaml
    try:
        typehint_def = load_typehint(plugin_path)
    except ValueError as e:
        errors.append(str(e))
        return False, config, errors, warnings
    
    # If no typehint file, config is valid by default
    if typehint_def is None:
        warnings.append("No config.typehint.yaml found, skipping typehint validation")
        return True, config, errors, warnings
    
    # Step 3: Validate config against typehint using TypeHintValidator
    # Convert FlowPluginConfig to dict for validator
    config_dict = config.model_dump()
    
    validator = TypeHintValidator(
        typehint_def=typehint_def,
        flow_config=config_dict,
        global_config=global_config
    )
    
    is_valid = validator.validate()
    errors.extend(validator.get_errors())
    warnings.extend(validator.get_warnings())
    
    return is_valid, config, errors, warnings




def load_pyproject_metadata(plugin_path: Path) -> FlowPluginMetadata:
    """
    Load plugin metadata from pyproject.toml.
    
    Args:
        plugin_path: Path to the flow plugin root directory
        
    Returns:
        FlowPluginMetadata object with plugin information
        
    Raises:
        FileNotFoundError: If pyproject.toml does not exist
        ValueError: If pyproject.toml is invalid TOML
    """
    pyproject_path = plugin_path / "pyproject.toml"
    
    if not pyproject_path.exists():
        raise FileNotFoundError(f"pyproject.toml not found in {plugin_path}")
    
    try:
        with open(pyproject_path, 'rb') as f:
            pyproject_data = tomllib.load(f)
    except Exception as e:
        raise ValueError(f"Invalid TOML in pyproject.toml: {e}")
    
    # Extract project information
    project_info = pyproject_data.get("project", {})
    
    # Get metadata with fallbacks
    name = project_info.get("name", plugin_path.name)
    version = project_info.get("version", "0.0.0")
    description = project_info.get("description")
    
    # Extract author from authors list
    authors = project_info.get("authors", [])
    author = None
    if authors and len(authors) > 0:
        author = authors[0].get("name")
    
    return FlowPluginMetadata(
        name=name,
        version=version,
        description=description,
        author=author
    )


def import_flow_module(plugin_path: Path, plugin_name: str, plugin_version: str) -> Any:
  """
  Import src/main.py from flow plugin.
  
  Args:
      plugin_path: Path to the flow plugin root directory
      plugin_name: Plugin name from pyproject.toml
      plugin_version: Plugin version from pyproject.toml
  
  Returns:
      Imported module
      
  Raises:
      FileNotFoundError: If src/main.py does not exist
      SyntaxError: If main.py has syntax errors
  """
  import importlib.util
  import sys
  
  src_path = plugin_path / "src"
  main_path = src_path / "main.py"
  
  if not main_path.exists():
      raise FileNotFoundError(f"src/main.py not found in {plugin_path}")
  
  # Create a unique package name using pyproject.toml name and version
  # Format: {name}_{version} as valid Python module name (replace - and . with _)
  safe_name = plugin_name.replace('-', '_').replace('.', '_')
  safe_version = plugin_version.replace('-', '_').replace('.', '_')
  package_name = f"{safe_name}_{safe_version}"
  module_name = f"{package_name}.main"
  
  # Track if we created __init__.py temporarily
  created_init = False
  src_init = src_path / "__init__.py"
  
  # If src doesn't have __init__.py, create one temporarily
  if not src_init.exists():
      src_init.write_text("")
      created_init = True
  
  # Load the module
  try:
      # Load src as a package first
      src_spec = importlib.util.spec_from_file_location(package_name, src_init)
      if src_spec is None or src_spec.loader is None:
          raise ImportError(f"Cannot load package from {src_path}")
      
      src_package = importlib.util.module_from_spec(src_spec)
      sys.modules[package_name] = src_package
      src_spec.loader.exec_module(src_package)
      
      # Load main.py as a submodule of src package
      spec = importlib.util.spec_from_file_location(module_name, main_path)
      if spec is None or spec.loader is None:
          raise ImportError(f"Cannot load module from {main_path}")
      
      module = importlib.util.module_from_spec(spec)
      sys.modules[module_name] = module
      
      # Set __package__ to enable relative imports
      module.__package__ = package_name
      
      spec.loader.exec_module(module)
      
      return module
  except SyntaxError as e:
      raise SyntaxError(f"Syntax error in main.py: {e}")
  except Exception as e:
      raise ImportError(f"Failed to import main.py: {e}")
  finally:
      # Clean up: remove temporary __init__.py if we created it
      if created_init and src_init.exists():
          try:
              src_init.unlink()
          except Exception:
              pass  # Ignore cleanup errors

def load_plugin(
    plugin_path: Path,
    global_config: Dict[str, Any]
) -> PluginLoadResult:
  """
  Load a flow plugin from the given path.
  
  Args:
      plugin_path: Path to the flow plugin root directory
      global_config: Global madousho configuration
      
  Returns:
      PluginLoadResult with success/failure status and plugin info
  """
  from .base import get_flow_class
  
  all_errors = []
  all_warnings = []
  
  # 1. Validate flow config (independent of global config)
  config_valid, flow_config, config_errors, config_warnings = validate_flow_config(
      plugin_path, global_config
  )
  all_errors.extend(config_errors)
  all_warnings.extend(config_warnings)
  
  if not config_valid:
      return PluginLoadResult.failure_result(all_errors, all_warnings)
  
  # 2. Load pyproject.toml for metadata
  try:
      metadata = load_pyproject_metadata(plugin_path)
  except FileNotFoundError as e:
      all_errors.append(str(e))
      return PluginLoadResult.failure_result(all_errors, all_warnings)
  except ValueError as e:
      all_errors.append(str(e))
      return PluginLoadResult.failure_result(all_errors, all_warnings)
  
  # 3. Import src/main.py
  try:
      main_module = import_flow_module(plugin_path, metadata.name, metadata.version)
  except FileNotFoundError as e:
      all_errors.append(str(e))
      return PluginLoadResult.failure_result(all_errors, all_warnings)
  except (SyntaxError, ImportError) as e:
      all_errors.append(str(e))
      return PluginLoadResult.failure_result(all_errors, all_warnings)
  
  # 4. Get FlowClass and instantiate flow
  try:
      flow_class = get_flow_class(main_module)
      
      # Instantiate flow (pass flow config and global config)
      flow_instance = flow_class(
          flow_config=flow_config.model_dump(),
          global_config=global_config
      )
      
  except ValueError as e:
      all_errors.append(str(e))
      return PluginLoadResult.failure_result(all_errors, all_warnings)
  except Exception as e:
      all_errors.append(f"Failed to instantiate flow: {e}")
      return PluginLoadResult.failure_result(all_errors, all_warnings)
  
  # 5. Create FlowPlugin and return success
  plugin = FlowPlugin(
      metadata=metadata,
      path=plugin_path,
      config=flow_config,
      flow_class=flow_class,
      flow_instance=flow_instance
  )
  
  return PluginLoadResult.success_result(plugin, all_warnings)
