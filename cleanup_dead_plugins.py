#!/usr/bin/env python3
"""
Dead Plugin Cleanup Script

This script removes identified dead plugins from listing.json based on
the modernization analysis. Plugins that haven't been updated since 2019
are considered dead and will be removed.
"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Dead plugins identified in the analysis (not updated since 2019)
DEAD_PLUGINS = {
    "bkerler/annotate",  # Annotate Functions - 2019-07-09
    "Vasco-jofra/format-string-finder-binja",  # Format String Finder - 2019-07-15
    "whitequark/binja_function_abi",  # Function ABI - 2019-11-22
    "whitequark/binja-i8086",  # Intel 8086 Architecture - 2019-09-04
    "Vasco-jofra/jump-table-branch-editor",  # Jump table branch editor - 2019-07-06
    "0x1F9F1/binja-msvc",  # MSVC - 2019-07-12
    "mechanicalnull/sourcery_pane",  # Sourcery Pane - 2019-07-15
    "carstein/Syscaller",  # Syscaller - 2019-07-15
    "verylazyguy/binaryninja-vmndh",  # VMNDH-2k12 Architecture Plugin - 2019-07-10
    "shareef12/driveranalyzer",  # Windows Driver Analyzer - 2019-08-08
}

# Stale plugins (not updated since 2020) - mark for review but don't remove yet
STALE_PLUGINS = {
    "404d/autoutils",  # Auto Utils - 2020-12-12
    "janbbeck/CleanTricks",  # Clean Tricks - 2020-06-08
    "toolCHAINZ/DUMB",  # DUMB - 2020-03-01
    "kryptoslogic/binja_degobfuscate",  # DeGObfuscate - 2020-12-02
    "shizmob/binja-depanalyzer",  # Dependency analyzer - 2020-05-25
    "mauronz/binja-emotet",  # Emotet API+string deobfuscator - 2020-09-21
    "chame1eon/binaryninja-frida",  # Frida - 2020-06-01
    "hugsy/gef-binja",  # GEF-Binja - 2020-05-18
    "icecr4ck/bnGB",  # Game Boy Loader and Architecture Plugin - 2020-11-17
    "d-we/binja-golang-symbol-restore",  # Golang Symbol Restore - 2020-10-19
}

def load_listing() -> List[Dict[str, Any]]:
    """Load the current listing.json file."""
    listing_path = Path("listing.json")
    if not listing_path.exists():
        logger.error("listing.json not found")
        return []
    
    try:
        with open(listing_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load listing.json: {e}")
        return []

def save_listing(listing: List[Dict[str, Any]]) -> bool:
    """Save the updated listing.json file."""
    listing_path = Path("listing.json")
    backup_path = Path(f"listing.json.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    
    try:
        # Create backup
        if listing_path.exists():
            listing_path.rename(backup_path)
            logger.info(f"Created backup: {backup_path}")
        
        # Save updated listing
        with open(listing_path, 'w', encoding='utf-8') as f:
            json.dump(listing, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Updated listing.json saved")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save listing.json: {e}")
        # Restore backup if save failed
        if backup_path.exists():
            backup_path.rename(listing_path)
            logger.info("Restored backup due to save failure")
        return False

def cleanup_dead_plugins(dry_run: bool = False) -> None:
    """
    Remove dead plugins from listing.json.
    
    Args:
        dry_run: If True, only show what would be removed without making changes
    """
    listing = load_listing()
    if not listing:
        return
    
    original_count = len(listing)
    removed_plugins = []
    stale_plugins_found = []
    
    # Filter out dead plugins
    updated_listing = []
    for plugin in listing:
        plugin_name = plugin.get("name", "")
        
        if plugin_name in DEAD_PLUGINS:
            removed_plugins.append(plugin_name)
            logger.warning(f"{'[DRY RUN] Would remove' if dry_run else 'Removing'} dead plugin: {plugin_name}")
        elif plugin_name in STALE_PLUGINS:
            stale_plugins_found.append(plugin_name)
            logger.info(f"Found stale plugin (keeping for now): {plugin_name}")
            updated_listing.append(plugin)
        else:
            updated_listing.append(plugin)
    
    # Report results
    logger.info(f"\n{'=== DRY RUN RESULTS ===' if dry_run else '=== CLEANUP RESULTS ==='}")
    logger.info(f"Original plugin count: {original_count}")
    logger.info(f"Dead plugins {'would be removed' if dry_run else 'removed'}: {len(removed_plugins)}")
    logger.info(f"Stale plugins found (kept): {len(stale_plugins_found)}")
    logger.info(f"Final plugin count: {len(updated_listing)}")
    
    if removed_plugins:
        logger.info(f"\n{'Plugins that would be removed:' if dry_run else 'Removed plugins:'}")
        for plugin in removed_plugins:
            logger.info(f"  - {plugin}")
    
    if stale_plugins_found:
        logger.info(f"\nStale plugins (review recommended):")
        for plugin in stale_plugins_found:
            logger.info(f"  - {plugin}")
    
    # Save changes if not dry run
    if not dry_run and removed_plugins:
        if save_listing(updated_listing):
            logger.info(f"\nSuccessfully cleaned up {len(removed_plugins)} dead plugins!")
        else:
            logger.error("Failed to save changes")
    elif dry_run:
        logger.info(f"\nDry run completed. Use --execute to apply changes.")
    else:
        logger.info(f"\nNo dead plugins found to remove.")

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Clean up dead plugins from listing.json")
    parser.add_argument("--execute", action="store_true", 
                       help="Actually remove plugins (default is dry run)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    dry_run = not args.execute
    
    if dry_run:
        logger.info("Running in DRY RUN mode. Use --execute to apply changes.")
    else:
        logger.warning("EXECUTING cleanup - plugins will be permanently removed!")
        response = input("Are you sure you want to continue? (yes/no): ")
        if response.lower() != 'yes':
            logger.info("Cleanup cancelled.")
            return
    
    cleanup_dead_plugins(dry_run=dry_run)

if __name__ == "__main__":
    main()