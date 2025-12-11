#!/usr/bin/env python3
"""
Script to remove dead/obsolete plugins from plugins.json

Usage:
    python scripts/remove_dead_plugins.py --dry-run  # Show what would be removed
    python scripts/remove_dead_plugins.py            # Actually remove plugins
"""

import json
import argparse
import sys
from pathlib import Path

# Plugins to remove (Phase 1: Low Risk)
PLUGINS_TO_REMOVE = [
    # Example/Tutorial plugins
    {
        'name': 'DUMB',
        'reason': 'Example plugin, not meant for production use'
    },
    {
        'name': 'VMNDH-2k12 Architecture Plugin',
        'reason': 'Example architecture from CTF challenge, not real-world'
    },
    # Obsolete malware-specific plugins
    {
        'name': 'Emotet API+string deobfuscator',
        'reason': 'Emotet botnet was taken down in 2021, plugin is obsolete'
    }
]

def load_plugins(filepath):
    """Load plugins from JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_plugins(filepath, plugins):
    """Save plugins to JSON file with nice formatting"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(plugins, f, indent=2, ensure_ascii=False)
        f.write('\n')  # Add trailing newline

def remove_plugins(plugins, plugins_to_remove, dry_run=False):
    """Remove specified plugins from the list"""
    plugins_to_remove_names = {p['name'] for p in plugins_to_remove}
    removed_plugins = []
    remaining_plugins = []
    
    for plugin in plugins:
        if plugin.get('name') in plugins_to_remove_names:
            removed_plugins.append(plugin)
            if not dry_run:
                print(f"✓ Removed: {plugin['name']}")
            else:
                print(f"Would remove: {plugin['name']}")
                reason = next(p['reason'] for p in plugins_to_remove if p['name'] == plugin['name'])
                print(f"  Reason: {reason}")
                print(f"  Last Updated: {plugin.get('lastUpdated', 'Unknown')}")
                print(f"  Author: {plugin.get('author', 'Unknown')}")
                print(f"  URL: {plugin.get('projectUrl', 'Unknown')}")
                print()
        else:
            remaining_plugins.append(plugin)
    
    return remaining_plugins, removed_plugins

def main():
    parser = argparse.ArgumentParser(description='Remove dead plugins from plugins.json')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be removed without actually removing')
    parser.add_argument('--plugins-file', default='plugins.json',
                       help='Path to plugins.json file (default: plugins.json)')
    
    args = parser.parse_args()
    
    # Get the repository root (parent of scripts directory)
    repo_root = Path(__file__).parent.parent
    plugins_file = repo_root / args.plugins_file
    
    if not plugins_file.exists():
        print(f"Error: {plugins_file} not found", file=sys.stderr)
        return 1
    
    # Load current plugins
    print(f"Loading plugins from {plugins_file}")
    plugins = load_plugins(plugins_file)
    original_count = len(plugins)
    print(f"Found {original_count} plugins\n")
    
    # Remove dead plugins
    if args.dry_run:
        print("DRY RUN MODE - No changes will be made\n")
        print("=" * 80)
        print("Plugins that would be removed:")
        print("=" * 80)
    else:
        print("=" * 80)
        print("Removing dead plugins:")
        print("=" * 80)
    
    remaining_plugins, removed_plugins = remove_plugins(
        plugins, PLUGINS_TO_REMOVE, dry_run=args.dry_run
    )
    
    # Summary
    print("\n" + "=" * 80)
    print("Summary:")
    print("=" * 80)
    print(f"Original plugin count: {original_count}")
    print(f"Plugins removed: {len(removed_plugins)}")
    print(f"Remaining plugins: {len(remaining_plugins)}")
    
    if removed_plugins:
        print("\nRemoved plugins:")
        for plugin in removed_plugins:
            reason = next(p['reason'] for p in PLUGINS_TO_REMOVE 
                         if p['name'] == plugin['name'])
            print(f"  - {plugin['name']}: {reason}")
    
    # Save if not dry run
    if not args.dry_run:
        print(f"\nSaving updated plugins to {plugins_file}")
        save_plugins(plugins_file, remaining_plugins)
        print("✓ Done!")
    else:
        print("\nDRY RUN - No changes made. Run without --dry-run to apply changes.")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
