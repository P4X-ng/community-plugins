#!/usr/bin/env python3
"""
Binary Ninja Plugin Metadata Generator

This script helps in the process of creating required metadata to add a plugin 
to the Binary Ninja plugin repository.
"""
import json
import argparse
import os
import io
import datetime
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Configuration constants
CURRENT_PLUGIN_METADATA_VERSION = 2
VALID_PLUGIN_TYPES = ["core", "ui", "binaryview", "architecture", "helper"]
VALID_APIS = ["python3"]  # Removed python2 support
VALID_PLATFORMS = ["Darwin", "Windows", "Linux"]
REQUIRED_LICENSE_KEYS = ["name", "text"]

def validate_list(data: Dict[str, Any], name: str, valid_list: List[str]) -> bool:
    """
    Validate that a field exists and contains valid list values.
    
    Args:
        data: Data dictionary to validate
        name: Field name to check
        valid_list: List of valid values
        
    Returns:
        True if validation passes, False otherwise
    """
    if name not in data:
        logger.warning(f"'{name}' field doesn't exist")
        return False
    elif not isinstance(data[name], list):
        logger.error(f"'{name}' field isn't a list")
        return False

    success = True
    for item in data[name]:
        if item not in valid_list:
            logger.error(f"plugin {name}: {item} not one of {valid_list}")
            success = False
    return success

def validate_string(data: Dict[str, Any], name: str) -> bool:
    """
    Validate that a field exists and is a string.
    
    Args:
        data: Data dictionary to validate
        name: Field name to check
        
    Returns:
        True if validation passes, False otherwise
    """
    if name not in data:
        logger.error(f"'{name}' field doesn't exist")
        return False
    elif not isinstance(data[name], str):
        logger.error(f"'{name}' field is {type(data[name])} not a string")
        return False
    return True

def validate_integer(data: Dict[str, Any], name: str) -> bool:
    """
    Validate that a field exists and is an integer.
    
    Args:
        data: Data dictionary to validate
        name: Field name to check
        
    Returns:
        True if validation passes, False otherwise
    """
    if name not in data:
        logger.error(f"'{name}' field doesn't exist.")
        return False
    elif not isinstance(data[name], int):
        logger.error(f"'{name}' is {type(data[name])} not an integer value")
        return False
    return True

def validate_string_map(data: Dict[str, Any], name: str, valid_keys: List[str], 
                       required_keys: Optional[List[str]] = None) -> bool:
    """
    Validate that a field exists and is a dictionary with valid keys.
    
    Args:
        data: Data dictionary to validate
        name: Field name to check
        valid_keys: List of valid keys for the dictionary
        required_keys: List of required keys (optional)
        
    Returns:
        True if validation passes, False otherwise
    """
    if name not in data:
        logger.error(f"'{name}' field doesn't exist.")
        return False
    elif not isinstance(data[name], dict):
        logger.error(f"'{name}' is {type(data[name])} not a dict type")
        return False

    success = True
    if required_keys is not None:
        for key in required_keys:
            if key not in data[name]:
                logger.error(f"required subkey '{key}' not in {name}")
                success = False

    for key in data[name].keys():
        if key not in valid_keys:
            logger.error(f"key '{key}' is not in the set of valid keys {valid_keys}")
            success = False

    return success

def validate_required_fields(data: Dict[str, Any]) -> bool:
    """
    Validate all required fields in plugin metadata.
    
    Args:
        data: Plugin metadata dictionary
        
    Returns:
        True if all validations pass, False otherwise
    """
    success = validate_integer(data, "pluginmetadataversion")
    if success:
        if data["pluginmetadataversion"] != CURRENT_PLUGIN_METADATA_VERSION:
            logger.error("'pluginmetadataversion' is not the correct version")
            success = False
    else:
        logger.info(f"Current version is {CURRENT_PLUGIN_METADATA_VERSION}")

    success &= validate_string(data, "name")
    success &= validate_list(data, "type", VALID_PLUGIN_TYPES)
    success &= validate_list(data, "api", VALID_APIS)
    success &= validate_string(data, "description")
    success &= validate_string(data, "longdescription")
    success &= validate_string_map(data, "license", REQUIRED_LICENSE_KEYS, REQUIRED_LICENSE_KEYS)
    valid_platform_list = validate_list(data, "platforms", VALID_PLATFORMS)
    success &= valid_platform_list
    success &= validate_string_map(data, "installinstructions", VALID_PLATFORMS, 
                                  list(data["platforms"]) if valid_platform_list else None)
    success &= validate_string(data, "version")
    success &= validate_string(data, "author")
    success &= validate_integer(data, "minimumbinaryninjaversion")
    return success

def get_combination_selection(valid_list: List[str], prompt: str, max_items: Optional[int] = None) -> List[str]:
    """
    Get user selection from a list of valid options.
    
    Args:
        valid_list: List of valid options
        prompt: Prompt to display to user
        max_items: Maximum number of items to select (optional)
        
    Returns:
        List of selected items
    """
    if max_items is None:
        max_items = len(valid_list)

    prompt2 = "Enter comma separated list of items> "
    if max_items == 1:
        prompt2 = "> "
        
    while True:
        print(prompt)
        for i, item in enumerate(valid_list):
            print(f"\t{i:>3}: {item}")
        items = filter(None, input(prompt2).split(","))
        result = []
        success = True
        
        for item in items:
            try:
                value = int(item.strip())
            except ValueError:
                logger.error(f"Couldn't convert {item} to integer")
                success = False
                break
                
            if value < 0 or value >= len(valid_list):
                logger.error(f"{value} is not a valid selection")
                success = False
                break
            else:
                result.append(valid_list[value])
                
        if success:
            return result

# License templates
LICENSE_TYPES = {
    "MIT": """Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.""",
    
    "2-Clause BSD": """Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.""",
    
    "Apache-2.0": """Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.""",
    
    "LGPL-2.0": """This library is free software; you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation; either version 2   of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with this library; if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA""",
    
    "LGPL-2.1": """This library is free software; you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation; either version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with this library; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA""",
    
    "LGPL-3.0": """This library is free software; you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation; either version 3.0 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with this library; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA""",
    
    "GPL-2.0": """This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, see <http://www.gnu.org/licenses/>.""",
    
    "GPL-3.0": """This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses/>."""
}

def generate_plugin_metadata() -> Dict[str, Any]:
    """
    Interactively generate plugin metadata.
    
    Returns:
        Dictionary containing plugin metadata
    """
    data = {}
    data["pluginmetadataversion"] = CURRENT_PLUGIN_METADATA_VERSION
    data["name"] = input("Enter plugin name: ")
    data["author"] = input("Enter your name or the name you want this plugin listed under: ")
    data["type"] = get_combination_selection(VALID_PLUGIN_TYPES, "Which types of plugin is this? ")
    data["api"] = get_combination_selection(VALID_APIS, "Which api's are supported? ")
    data["description"] = input("Enter a short description of this plugin (50 characters max): ")
    data["longdescription"] = input("Enter a full description of this plugin (Markdown formatted): ")
    data["license"] = {}

    license_type_names = ["Other"] + list(LICENSE_TYPES.keys())
    data["license"]["name"] = get_combination_selection(license_type_names, "Enter the license type of this plugin:", 1)[0]
    
    if data["license"]["name"] == "Other":
        data["license"]["name"] = input("Enter License Type: ")
        data["license"]["text"] = input("Enter License Text: ")
    else:
        data["license"]["text"] = LICENSE_TYPES[data["license"]["name"]]

    year = datetime.datetime.now().year
    holder = data["author"]

    answer = input(f"Is this the correct copyright information?\n\tCopyright {year} {holder}\n[Y/n]: ")
    if answer not in ("Y", "y", ""):
        year = input("Enter copyright year: ")
        holder = input("Enter copyright holder: ")

    data["license"]["text"] = f"Copyright {year} {holder}\n\n" + data["license"]["text"]
    data["platforms"] = get_combination_selection(VALID_PLATFORMS, "Which platforms are supported? ")

    data["installinstructions"] = {}
    for platform in data["platforms"]:
        print("Enter Markdown formatted installation directions for the following platform: ")
        data["installinstructions"][platform] = input(f"{platform}: ")
        
    data["version"] = input("Enter the version string for this plugin. ")
    data["minimumbinaryninjaversion"] = int(input("Enter the minimum build number that you've successfully tested this plugin with: "))
    return data


readme_template = """# {name} (v{version})
Author: **{author}**

_{description}_

## Description:

{longdescription}
{install}

## Minimum Version

This plugin requires the following minimum version of Binary Ninja:

* {minimum}

{dependencies}
## License

This plugin is released under a {license} license.
## Metadata Version

{metadataVersion}
"""

def generate_readme(plugin: Dict[str, Any]) -> str:
    """
    Generate README content from plugin metadata.
    
    Args:
        plugin: Plugin metadata dictionary
        
    Returns:
        README content as string
    """
    install = None
    if "installinstructions" in plugin:
        install = "\n\n## Installation Instructions"
        for platform in plugin["installinstructions"]:
            install += f"\n\n### {platform}\n\n{plugin['installinstructions'][platform]}"

    dependencies = ""
    if "dependencies" in plugin:
        dependencies = "\n\n## Required Dependencies\n\nThe following dependencies are required for this plugin:\n\n"
        for dependency in plugin["dependencies"]:
            dependency_list = ", ".join(plugin["dependencies"][dependency])
            dependencies += f" * {dependency} - {dependency_list}\n"
        dependencies += "\n"

    return readme_template.format(
        name=plugin["name"], 
        version=plugin["version"],
        author=plugin["author"], 
        description=plugin["description"],
        longdescription=plugin["longdescription"], 
        install=install or "",
        minimum=plugin["minimumbinaryninjaversion"], 
        dependencies=dependencies,
        license=plugin["license"]["name"], 
        metadataVersion=plugin["pluginmetadataversion"]
    )

def main():
    """Main function for plugin metadata generation."""
    parser = argparse.ArgumentParser(description="Generate README.md (and optional LICENSE) from plugin.json metadata")
    parser.add_argument("-a", "--all", help="Generate all supporting information needed (plugin.json, README.md, LICENSE)", action="store_true")
    parser.add_argument("-p", "--plugin", help="Interactively generate plugin.json file", action="store_true")
    parser.add_argument("-r", "--readme", help="Automatically generate README.md", action="store_true")
    parser.add_argument("-l", "--license", help="Automatically generate LICENSE file", action="store_true")
    parser.add_argument("-f", "--force", help="Force overwrite of existing files", action="store_true")
    parser.add_argument("-v", "--validate", help="Validate existing plugin.json only", metavar="JSON")
    args = parser.parse_args()

    # Just validate an existing plugin.json
    if args.validate is not None:
        try:
            with open(args.validate, "r", encoding="utf8") as f:
                plugin_data = json.load(f)
            if validate_required_fields(plugin_data):
                logger.info("Successfully validated json file")
                return 0
            else:
                logger.error("JSON validation failed")
                return 1
        except Exception as e:
            logger.error(f"Failed to load or validate {args.validate}: {e}")
            return 1

    plugin_json_path = Path("plugin.json")

    # Enable all the options if --all is selected
    if args.all:
        args.plugin = True
        args.readme = True
        args.license = True

    if args.plugin:
        plugin = generate_plugin_metadata()
    else:
        try:
            with open(plugin_json_path, "r", encoding="utf8") as f:
                plugin = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"File {plugin_json_path} doesn't contain valid json: {e}")
            return 1
        except FileNotFoundError:
            logger.error(f"File {plugin_json_path} doesn't exist")
            return 1
        except Exception as e:
            logger.error(f"Failed to load {plugin_json_path}: {e}")
            return 1

    logger.info("-" * 65)
    if validate_required_fields(plugin):
        logger.info("Successfully validated json file")
    else:
        logger.error("JSON validation failed")
        return 1

    # Note: Removed Python 2 deprecation warning as we no longer support it

    if args.plugin:
        skip = False
        logger.info("-" * 65)
        if plugin_json_path.exists() and not args.force:
            logger.info(f"{plugin_json_path} already exists.")
            response = input("Overwrite it? (N,y) ")
            if response != "y":
                logger.info("Not overwriting plugin.json")
                skip = True
        if not skip:
            logger.info("Creating plugin.json.")
            try:
                with open(plugin_json_path, "w", encoding="utf8") as plugin_file:
                    json.dump(plugin, plugin_file, indent=4, ensure_ascii=False)
            except Exception as e:
                logger.error(f"Failed to write plugin.json: {e}")
                return 1

    if args.readme:
        logger.info("-" * 65)
        readme_path = Path("README.md")
        skip = False
        if readme_path.exists() and not args.force:
            logger.info(f"{readme_path} already exists.")
            response = input("Overwrite it? (N,y) ")
            if response != "y":
                logger.info("Not overwriting README.md")
                skip = True
        if not skip:
            logger.info("Creating README.md")
            try:
                with open(readme_path, "w", encoding="utf8") as readme_file:
                    readme_file.write(generate_readme(plugin))
            except Exception as e:
                logger.error(f"Failed to write README.md: {e}")
                return 1

    if args.license:
        logger.info("-" * 65)
        license_path = Path("LICENSE")
        skip = False
        if license_path.exists() and not args.force:
            logger.info(f"{license_path} already exists.")
            response = input("Overwrite it? (N,y) ")
            if response != "y":
                logger.info("Not overwriting LICENSE")
                skip = True
        if not skip:
            logger.info("Creating LICENSE")
            try:
                with open(license_path, "w", encoding="utf8") as license_file:
                    license_file.write(plugin["license"]["text"])
            except Exception as e:
                logger.error(f"Failed to write LICENSE: {e}")
                return 1

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
