#!/usr/bin/env python3
"""
Binary Ninja Plugin Repository Index Generator

This script generates the plugin index by fetching metadata from GitHub repositories
and creating the plugins.json file and README.md table.
"""
import sys
import os
import json
import argparse
import base64
import requests
from dateutil import parser
import re
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('plugin_generation.log')
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class Config:
    """Configuration constants for the plugin generator."""
    CURRENT_PLUGIN_METADATA_VERSION: int = 2
    MAX_DESCRIPTION_LENGTH: int = 100
    PROGRESS_BAR_LENGTH: int = 60
    PROGRESS_BAR_FILL: str = '█'
    GITHUB_API_BASE: str = "https://api.github.com"
    GITHUB_SITE_BASE: str = "https://github.com"
    RATE_LIMIT_DELAY: float = 0.1  # Delay between API calls
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 1.0

config = Config()

class GitHubAPIError(Exception):
    """Custom exception for GitHub API errors."""
    pass

class PluginProcessingError(Exception):
    """Custom exception for plugin processing errors."""
    pass

def print_progress_bar(iteration: int, total: int, prefix: str = '', 
                      length: int = None, fill: str = None) -> None:
    """
    Display a progress bar in the terminal.
    
    Args:
        iteration: Current iteration
        total: Total iterations
        prefix: Prefix string
        length: Length of progress bar
        fill: Fill character
    """
    if length is None:
        length = config.PROGRESS_BAR_LENGTH
    if fill is None:
        fill = config.PROGRESS_BAR_FILL
        
    filled_length = int(length * iteration // total)
    bar = (fill * filled_length) + ('-' * (length - filled_length))
    percent = 100 * (iteration / float(total))
    fmt = f"\r{prefix} |{bar}| {percent:.1f}%"
    sys.stdout.write(fmt)
    sys.stdout.flush()
    
    # Print New Line on Complete
    if iteration == total:
        print()


class GitHubAPIClient:
    """GitHub API client with session management and rate limiting."""
    
    def __init__(self, token: str):
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'BinaryNinja-Plugin-Repository-Generator'
        })
        
    def get_file(self, url: str) -> requests.Response:
        """
        Get a file from GitHub API with retry logic and rate limiting.
        
        Args:
            url: GitHub API URL
            
        Returns:
            Response object
            
        Raises:
            GitHubAPIError: If API request fails after retries
        """
        for attempt in range(config.MAX_RETRIES):
            try:
                # Add rate limiting delay
                time.sleep(config.RATE_LIMIT_DELAY)
                
                response = self.session.get(url, timeout=30)
                
                # Check for rate limiting
                if response.status_code == 403 and 'rate limit' in response.text.lower():
                    reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                    current_time = int(time.time())
                    sleep_time = max(reset_time - current_time, 60)
                    logger.warning(f"Rate limited. Sleeping for {sleep_time} seconds.")
                    time.sleep(sleep_time)
                    continue
                    
                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt == config.MAX_RETRIES - 1:
                    raise GitHubAPIError(f"Failed to fetch {url} after {config.MAX_RETRIES} attempts: {e}")
                time.sleep(config.RETRY_DELAY * (2 ** attempt))  # Exponential backoff
                
        raise GitHubAPIError(f"Unexpected error fetching {url}")

# Global API client instance
api_client: Optional[GitHubAPIClient] = None


def get_plugin_json(plugin: Dict[str, Any], short_urls: Dict[str, str], debug: bool = False) -> Optional[Dict[str, Any]]:
    """
    Process a plugin entry and return its metadata.
    
    Args:
        plugin: Plugin configuration from listing.json
        short_urls: Cache of shortened URLs
        debug: Enable debug logging
        
    Returns:
        Plugin metadata dictionary or None if processing fails
    """
    if debug:
        logger.debug(f"Processing plugin: {plugin['name']}")
        
    try:
        if "site" in plugin:
            return _process_external_site_plugin(plugin, debug)
        else:
            return _process_github_plugin(plugin, short_urls, debug)
    except Exception as e:
        logger.error(f"Failed to process plugin {plugin['name']}: {e}")
        return None

def _process_external_site_plugin(plugin: Dict[str, Any], debug: bool) -> Optional[Dict[str, Any]]:
    """Process a plugin from an external site."""
    try:
        response = api_client.get_file(plugin["site"])
        plugins_json = response.json()
        
        for site_plugin in plugins_json:
            if site_plugin["name"] == plugin["name"]:
                return site_plugin
                
        logger.error(f'No plugin matching {plugin["name"]} found in {plugin["site"]}')
        return None
    except Exception as e:
        logger.error(f"Failed to process external site plugin {plugin['name']}: {e}")
        return None

def _process_github_plugin(plugin: Dict[str, Any], short_urls: Dict[str, str], debug: bool) -> Optional[Dict[str, Any]]:
    """Process a plugin from GitHub."""
    user_and_project = plugin["name"]
    user_name = user_and_project.split("/")[0]
    project_url = f"{config.GITHUB_API_BASE}/repos/{user_and_project}"
    
    view_only = plugin.get('view_only', False)
    auto_update = plugin.get('auto_update', False)
    
    # Get release data
    release_data = None
    if auto_update:
        release_data = _get_latest_release(project_url, plugin["name"])
        if release_data is None:
            return None
        plugin['tag'] = release_data['tag_name']
    elif not view_only:
        release_data = _get_specific_release(project_url, plugin["tag"], plugin["name"])
        if release_data is None:
            return None
    
    # Get commit and zip URL
    commit, zip_url = None, None
    if not view_only:
        commit, zip_url = _get_tag_info(project_url, plugin["tag"], plugin["name"])
        if commit is None:
            return None
    
    # Get project data
    project_data = _get_project_data(project_url, plugin["name"])
    if project_data is None:
        return None
    
    # Get plugin.json content
    plugin_json_data = _get_plugin_json_content(project_url, plugin, view_only, debug)
    if plugin_json_data is None:
        return None
    
    # Get requirements.txt if available
    requirements_txt = _get_requirements_txt(project_url, plugin, view_only)
    
    # Process URLs
    short_url = _process_urls(zip_url, short_urls, view_only)
    
    # Build final plugin data
    return _build_plugin_data(
        plugin_json_data, plugin, project_data, user_name, 
        release_data, zip_url, short_url, commit, requirements_txt, view_only
    )

def _get_latest_release(project_url: str, plugin_name: str) -> Optional[Dict[str, Any]]:
    """Get the latest release data for a plugin."""
    latest_release_url = f"{project_url}/releases/latest"
    
    try:
        response = api_client.get_file(latest_release_url)
        release_data = response.json()
        
        if release_data.get('message') == 'Not Found':
            logger.error(f"{plugin_name}: Couldn't get release information. "
                        "Likely the user created a tag but no associated release.")
            return None
        elif release_data.get('message') == 'Bad credentials':
            logger.error("Bad credentials, check access token.")
            return None
            
        return release_data
        
    except Exception as e:
        logger.error(f"Unable to get latest release for {plugin_name}: {e}")
        return None

def _get_specific_release(project_url: str, tag: str, plugin_name: str) -> Optional[Dict[str, Any]]:
    """Get specific release data for a plugin."""
    releases_url = f"{project_url}/releases/tags/{tag}"
    
    try:
        response = api_client.get_file(releases_url)
        release_data = response.json()
        
        if release_data.get("message") == "Not Found":
            logger.error(f"{plugin_name}: Couldn't get release information for tag {tag}. "
                        f"Tried URL: {releases_url}")
            return None
            
        return release_data
        
    except Exception as e:
        logger.error(f"Unable to get release for {plugin_name} tag {tag}: {e}")
        return None

def _get_tag_info(project_url: str, tag: str, plugin_name: str) -> tuple[Optional[str], Optional[str]]:
    """Get commit hash and zip URL for a specific tag."""
    tags_url = f"{project_url}/tags"
    
    try:
        response = api_client.get_file(tags_url)
        tag_data = response.json()
        
        for tag_info in tag_data:
            if tag_info["name"] == tag:
                return tag_info["commit"]["sha"], tag_info["zipball_url"]
                
        logger.error(f"Unable to associate tag {tag} with a commit for plugin {plugin_name}")
        return None, None
        
    except Exception as e:
        logger.error(f"Unable to get tag info for {plugin_name}: {e}")
        return None, None

def _get_project_data(project_url: str, plugin_name: str) -> Optional[Dict[str, Any]]:
    """Get project metadata from GitHub."""
    try:
        response = api_client.get_file(project_url)
        return response.json()
    except Exception as e:
        logger.error(f"Unable to get project data for {plugin_name}: {e}")
        return None

def _get_plugin_json_content(project_url: str, plugin: Dict[str, Any], view_only: bool, debug: bool) -> Optional[Dict[str, Any]]:
    """Get and parse plugin.json content from GitHub."""
    subdir = plugin.get("subdir", "")
    
    if subdir:
        if view_only:
            plugin_json_url = f"{project_url}/contents/{subdir}/plugin.json"
        else:
            plugin_json_url = f"{project_url}/contents/{subdir}/plugin.json?ref={plugin['tag']}"
    else:
        if view_only:
            plugin_json_url = f"{project_url}/contents/plugin.json"
        else:
            plugin_json_url = f"{project_url}/contents/plugin.json?ref={plugin['tag']}"
    
    try:
        if debug:
            logger.debug(f"Getting plugin.json from {plugin_json_url}")
            
        response = api_client.get_file(plugin_json_url)
        content = response.json()['content']
        data = json.loads(base64.b64decode(content))
        
        # Handle old-style plugin.json format
        if "plugin" in data:
            data = data["plugin"]
            
        # Try to get README if longdescription is missing or short
        if ('longdescription' in data and len(data['longdescription']) < config.MAX_DESCRIPTION_LENGTH) or ('longdescription' not in data):
            data = _add_readme_content(project_url, plugin, data, view_only)
            
        return data
        
    except Exception as e:
        logger.error(f"Unable to get plugin.json from {plugin_json_url}: {e}")
        return None

def _add_readme_content(project_url: str, plugin: Dict[str, Any], data: Dict[str, Any], view_only: bool) -> Dict[str, Any]:
    """Try to add README content as longdescription if missing."""
    readme_files = ["README.md", "README.MD", "readme.md", "README", "readme", "Readme.md"]
    subdir = plugin.get("subdir", "")
    
    if subdir:
        # Try both subdir and root level READMEs
        readme_files = [f"{subdir}/{x}" for x in readme_files] + readme_files
    
    for readme_file in readme_files:
        try:
            if view_only:
                readme_url = f"{project_url}/contents/{readme_file}"
            else:
                readme_url = f"{project_url}/contents/{readme_file}?ref={plugin['tag']}"
                
            response = api_client.get_file(readme_url)
            readme_json = response.json()
            
            if all(k in readme_json for k in ("encoding", "content")):
                if readme_json["encoding"] == "base64":
                    data['longdescription'] = base64.b64decode(readme_json["content"]).decode('utf-8')
                    break
        except Exception:
            # Continue trying other README files
            continue
            
    return data

def _get_requirements_txt(project_url: str, plugin: Dict[str, Any], view_only: bool) -> str:
    """Get requirements.txt content if available."""
    if view_only:
        return ""
        
    requirements_txt = ""
    subdir = plugin.get("subdir", "")
    
    try:
        if subdir:
            req_url = f"{project_url}/contents/{subdir}/requirements.txt?ref={plugin['tag']}"
            response = api_client.get_file(req_url)
            req_json = response.json()
            
            if "content" not in req_json:  # Try top-level requirements as well
                req_url = f"{project_url}/contents/requirements.txt?ref={plugin['tag']}"
                response = api_client.get_file(req_url)
                req_json = response.json()
        else:
            req_url = f"{project_url}/contents/requirements.txt?ref={plugin['tag']}"
            response = api_client.get_file(req_url)
            req_json = response.json()
            
        if "content" in req_json:
            requirements_txt = base64.b64decode(req_json["content"]).decode('utf-8')
            if requirements_txt.startswith("\ufeff"):  # Remove BOM
                requirements_txt = requirements_txt[1:]
            requirements_txt = requirements_txt.replace("\r\n", "\n")
            
    except Exception:
        # Requirements.txt is optional
        pass
        
    return requirements_txt

def _process_urls(zip_url: Optional[str], short_urls: Dict[str, str], view_only: bool) -> str:
    """Process and potentially shorten URLs."""
    if view_only or zip_url is None:
        return ""
        
    # Check if we already have a short URL for this zip URL
    if zip_url in short_urls:
        return short_urls[zip_url]
        
    # Try to use URL shortener if configured
    url_shortener = os.getenv("URL_SHORTENER")
    if url_shortener:
        try:
            json_data = {"cdn_prefix": "v35.us", "url_long": zip_url}
            response = requests.post(url_shortener, json=json_data, timeout=10)
            json_response = response.json()
            
            if json_response.get('error') == '':
                short_url = json_response.get("url_short", "")
                if short_url.startswith("http"):
                    return short_url
        except Exception as e:
            logger.warning(f"Failed to shorten URL {zip_url}: {e}")
            
    return ""

def _build_plugin_data(plugin_json_data: Dict[str, Any], plugin: Dict[str, Any], 
                      project_data: Dict[str, Any], user_name: str, 
                      release_data: Optional[Dict[str, Any]], zip_url: Optional[str], 
                      short_url: str, commit: Optional[str], requirements_txt: str, 
                      view_only: bool) -> Dict[str, Any]:
    """Build the final plugin data structure."""
    # Determine last updated timestamp
    if view_only:
        last_updated = int(parser.parse(project_data["updated_at"]).timestamp())
    else:
        last_updated = int(parser.parse(release_data["published_at"]).timestamp())
    
    # Add required fields
    plugin_json_data["lastUpdated"] = last_updated
    plugin_json_data["projectUrl"] = f"{config.GITHUB_SITE_BASE}/{plugin['name']}"
    plugin_json_data["projectData"] = project_data
    plugin_json_data["projectData"]["updated_at"] = datetime.fromtimestamp(last_updated, timezone.utc).isoformat()
    plugin_json_data["authorUrl"] = f"{config.GITHUB_SITE_BASE}/{user_name}"
    
    if view_only:
        plugin_json_data["packageUrl"] = "https://127.0.0.1/"
        plugin_json_data["packageShortUrl"] = "https://127.0.0.1/"
        plugin_json_data["view_only"] = True
    else:
        plugin_json_data["packageUrl"] = zip_url or ""
        plugin_json_data["packageShortUrl"] = short_url
        plugin_json_data["view_only"] = False
        
    plugin_json_data["dependencies"] = requirements_txt
    
    # Clean up the project name for path
    plugin_json_data["path"] = re.sub(r"[^a-zA-Z0-9_]", "", re.sub(r"/", "_", project_data["full_name"]))
    plugin_json_data["commit"] = commit
    
    # Normalize API field
    if "api" in plugin_json_data and isinstance(plugin_json_data["api"], str):
        plugin_json_data["api"] = [plugin_json_data["api"]]
    
    # Handle version fields
    if "minimumbinaryninjaversion" in plugin_json_data:
        if not isinstance(plugin_json_data["minimumbinaryninjaversion"], int):
            plugin_json_data["minimumBinaryNinjaVersion"] = 0
        else:
            plugin_json_data["minimumBinaryNinjaVersion"] = plugin_json_data["minimumbinaryninjaversion"]
        del plugin_json_data["minimumbinaryninjaversion"]
    elif "minimumBinaryNinjaVersion" in plugin_json_data:
        if not isinstance(plugin_json_data["minimumBinaryNinjaVersion"], int):
            plugin_json_data["minimumBinaryNinjaVersion"] = 0
    else:
        plugin_json_data["minimumBinaryNinjaVersion"] = 0
    
    # Set default values for missing fields
    if "pluginmetadataversion" not in plugin_json_data:
        plugin_json_data["pluginmetadataversion"] = config.CURRENT_PLUGIN_METADATA_VERSION
        
    if "maximumBinaryNinjaVersion" not in plugin_json_data or not isinstance(plugin_json_data["maximumBinaryNinjaVersion"], int):
        plugin_json_data["maximumBinaryNinjaVersion"] = 999999
        
    if "platforms" not in plugin_json_data:
        plugin_json_data["platforms"] = []
        
    if "installinstructions" not in plugin_json_data:
        plugin_json_data["installinstructions"] = {}
        
    if "subdir" in plugin:
        plugin_json_data["subdir"] = plugin["subdir"]
        
    # Native plugins require minimum version to avoid error logs
    if view_only and plugin_json_data["minimumBinaryNinjaVersion"] < 6135:
        plugin_json_data["minimumBinaryNinjaVersion"] = 6135
        
    return plugin_json_data

def main():
    """Main function to generate plugin index."""
    parser = argparse.ArgumentParser(description="Produce 'plugins.json' for plugin repository.")
    parser.add_argument("-i", "--initialize", action="store_true", default=False,
        help="For first time running the command against the old format")
    parser.add_argument("-r", "--readmeskip", action="store_true", default=False,
        help="Skip generating a README.md")
    parser.add_argument("-l", "--listing", action="store", default="listing.json")
    parser.add_argument("-d", "--debug", action="store_true", default=False,
        help="Debugging output")
    parser.add_argument("token", help="GitHub API token")
    args = parser.parse_args()
    
    # Set up logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize global API client
    global api_client
    api_client = GitHubAPIClient(args.token)
    
    plugins_json_path = Path("./plugins.json")
    
    # Load existing plugins for comparison
    old_plugins = {}
    short_urls = {}
    if plugins_json_path.exists():
        try:
            with open(plugins_json_path, encoding='utf-8') as plugins_file:
                existing_plugins = json.load(plugins_file)
                for plugin in existing_plugins:
                    # Create lookup for existing URLs to avoid duplication
                    if "packageShortUrl" in plugin and len(plugin["packageShortUrl"]) > 0:
                        short_urls[plugin["packageUrl"]] = plugin["packageShortUrl"]
                    old_plugins[plugin["projectData"]["full_name"]] = plugin["lastUpdated"]
        except Exception as e:
            logger.error(f"Failed to load existing plugins.json: {e}")
            return 1
    
    # Load plugin listing
    try:
        with open(args.listing, "r", encoding="utf-8") as listing_file:
            listing = json.load(listing_file)
    except Exception as e:
        logger.error(f"Failed to load listing file {args.listing}: {e}")
        return 1
    
    # Process all plugins
    all_plugins = {}
    logger.info(f"Processing {len(listing)} plugins...")
    
    for i, plugin in enumerate(listing):
        print_progress_bar(i, len(listing), prefix="Collecting Plugin JSON files:")
        json_data = get_plugin_json(plugin, short_urls, debug=args.debug)
        if json_data is not None:
            all_plugins[plugin["name"]] = json_data
        else:
            logger.warning(f"Failed to process plugin: {plugin['name']}")
    
    print_progress_bar(len(listing), len(listing), prefix="Collecting Plugin JSON files:")
    
    # Analyze changes
    new_plugins = []
    updated_plugins = []
    removed_plugins = []
    new_list = []
    
    for name, plugin_data in all_plugins.items():
        new_list.append(name)
        plugin_is_new = name not in old_plugins
        plugin_is_updated = False
        
        if not plugin_is_new:
            plugin_is_updated = plugin_data["lastUpdated"] > old_plugins[name]
        
        if plugin_is_updated or plugin_is_new:
            if plugin_is_new:
                new_plugins.append(name)
            elif plugin_is_updated:
                updated_plugins.append(name)
    
    for name in old_plugins:
        if name not in new_list:
            removed_plugins.append(name)
    
    # Convert to list for JSON output
    all_plugins_list = list(all_plugins.values())
    
    # Log summary
    logger.info(f"{len(new_plugins)} New Plugins:")
    for plugin in new_plugins:
        logger.info(f"\t- {plugin}")
    logger.info(f"{len(updated_plugins)} Updated Plugins:")
    for plugin in updated_plugins:
        logger.info(f"\t- {plugin}")
    logger.info(f"{len(removed_plugins)} Removed Plugins:")
    for plugin in removed_plugins:
        logger.info(f"\t- {plugin}")
    
    # Write plugins.json
    logger.info(f"Writing {plugins_json_path}")
    try:
        with open(plugins_json_path, "w", encoding='utf-8') as plugins_file:
            json.dump(all_plugins_list, plugins_file, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to write plugins.json: {e}")
        return 1
    
    # Generate README.md if requested
    if not args.readmeskip:
        try:
            _generate_readme(all_plugins)
        except Exception as e:
            logger.error(f"Failed to generate README.md: {e}")
            return 1
    
    logger.info("Plugin index generation completed successfully!")
    return 0

def _generate_readme(all_plugins: Dict[str, Dict[str, Any]]) -> None:
    """Generate README.md file with plugin table."""
    info = ""
    info_path = Path("INFO")
    if info_path.exists():
        info = info_path.read_text(encoding="utf-8") + "\n"
    
    readme_path = Path("README.md")
    with open(readme_path, "w", encoding="utf-8") as readme:
        readme.write("# Binary Ninja Plugins\n\n")
        readme.write("| PluginName | Author | Description | Last Updated | Type | API | License |\n")
        readme.write("|------------|--------|-------------|--------------|------|-----|---------|\n")
        
        # Sort plugins by name (case-insensitive)
        sorted_plugins = dict(sorted(all_plugins.items(), key=lambda x: x[1]['name'].casefold()))
        
        for plugin in sorted_plugins.values():
            api = plugin["api"][0] if "api" in plugin and isinstance(plugin["api"], list) and len(plugin["api"]) > 0 else "None"
            if "type" not in plugin:
                plugin['type'] = ["None"]
            
            # Format the table row
            readme.write(f"|[{plugin['name']}]({plugin['projectUrl']})"
                f"|[{plugin['author']}]({plugin['authorUrl']})"
                f"|{plugin['description']}"
                f"|{datetime.fromtimestamp(plugin['lastUpdated']).date()}"
                f"|{', '.join(sorted(plugin['type']))}"
                f"|{api}"
                f"|{plugin['license']['name']}|\n")
        
        readme.write(info)
    
    logger.info("README.md generated successfully")


if __name__ == "__main__":
    sys.exit(main())
