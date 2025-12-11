#!/usr/bin/env python3
"""
GitHub Issue Plugin Validation Script

This script validates plugin submissions from GitHub issues by checking
if the repository has valid releases and plugin.json files.
"""
import os
import sys
import requests
import base64
import json
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass

def get_file(url: str, token: str) -> requests.Response:
    """
    Get a file from GitHub API with proper error handling.
    
    Args:
        url: GitHub API URL
        token: GitHub API token
        
    Returns:
        Response object
        
    Raises:
        ValidationError: If request fails
    """
    try:
        response = requests.get(url, headers={'Authorization': f'token {token}'}, timeout=30)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        raise ValidationError(f"Failed to fetch {url}: {e}")

def validate_repo(line: str, token: str) -> None:
    """
    Validate a repository from a GitHub issue line.
    
    Args:
        line: Line from GitHub issue containing repository URL
        token: GitHub API token
        
    Raises:
        ValidationError: If validation fails
        SystemExit: On validation success or failure
    """
    # Extract repository name from line
    repo = line.split(" ")[-1].lower()  # handle both cases of just URL or with "Repo URL:" before
    repo = repo.replace("https://github.com/", "").strip().strip("/")  # just get the user/project portion
    
    if not repo or "/" not in repo:
        raise ValidationError(f"Invalid repository format: {repo}")
    
    project_url = f"https://api.github.com/repos/{repo}"
    latest_release_url = f"{project_url}/releases/latest"
    
    logger.info(f"Validating repository: {repo}")
    
    try:
        # Get latest release
        response = get_file(latest_release_url, token)
        release_data = response.json()
        
        # Check for error messages
        message = release_data.get('message')
        if message == 'Not Found':
            raise ValidationError(f"Repository {repo}: Couldn't get release information. "
                                "Likely the user created a tag but no associated release.")
        elif message == 'Bad credentials':
            raise ValidationError("Bad credentials, check access token.")
        elif message:
            raise ValidationError(f"GitHub API error: {message}")
            
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f"Failed to load valid release data from {latest_release_url}: {e}")
    
    try:
        # Get plugin.json from the release tag
        tag = release_data['tag_name']
        plugin_json_url = f"{project_url}/contents/plugin.json?ref={tag}"
        
        response = get_file(plugin_json_url, token)
        content = response.json()['content']
        json_content = json.loads(base64.b64decode(content))
        
        logger.info(f"Successfully validated repository {repo} with tag {tag}")
        
    except KeyError as e:
        raise ValidationError(f"Missing required field in API response: {e}")
    except json.JSONDecodeError as e:
        raise ValidationError(f"Failed to parse plugin.json from {repo}: {e}")
    except Exception as e:
        raise ValidationError(f"Failed to parse valid plugin.json from "
                            f"https://github.com/{repo}/blob/master/plugin.json: {e}")

def main():
    """Main function to validate plugin from GitHub issue."""
    if len(sys.argv) != 2:
        logger.error("Usage: python validate_json.py <github_token>")
        sys.exit(1)
        
    token = sys.argv[1]
    issue_content = os.environ.get("ISSUE_CONTENT")
    
    if not issue_content:
        logger.error("ISSUE_CONTENT environment variable not set")
        sys.exit(1)
    
    lines = issue_content.split("\n")
    
    # First, look for lines starting with "Repo URL:"
    for line in lines:
        if line.startswith("Repo URL:"):
            try:
                validate_repo(line, token)
                logger.info("Validation successful!")
                sys.exit(0)
            except ValidationError as e:
                logger.error(str(e))
                sys.exit(1)
    
    # If no "Repo URL:" found, look for the first GitHub URL
    for line in lines:
        if line.startswith("https://github.com/"):
            try:
                validate_repo(line, token)
                logger.info("Validation successful!")
                sys.exit(0)
            except ValidationError as e:
                logger.error(str(e))
                sys.exit(1)
    
    logger.error("No GitHub repository URL found in issue content")
    sys.exit(1)

if __name__ == "__main__":
    main()

