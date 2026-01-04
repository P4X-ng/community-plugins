# Community Plugins Analysis - Dead and Outdated Plugins

**Analysis Date:** 2025-12-11  
**Total Plugins Analyzed:** 178  
**Plugins Requiring Attention:** 36

## Executive Summary

This analysis identifies plugins in the Binary Ninja community repository that are potentially dead, unmaintained, or obsolete. Out of 178 total plugins, 36 require attention:

- **3 plugins** are definitively obsolete and should be removed
- **31 plugins** haven't been updated in over 5 years and likely don't work with modern Binary Ninja
- **18 plugins** still support Python 2 (deprecated) and are over 4 years old

## Methodology

Plugins were analyzed based on:
1. **Last Update Date** - When the plugin was last modified
2. **Python Version Support** - Python 2 is deprecated and indicates lack of maintenance
3. **Use Case Relevance** - Some plugins target obsolete malware families or are example code
4. **Age Threshold** - Plugins >5 years old without updates are likely broken with modern BN versions

## Recommendations by Category

### Category 1: DEFINITELY REMOVE (3 plugins)

These plugins are no longer relevant or are example code never meant for production use.

#### 1.1 Malware-Family-Specific Plugins

| Plugin Name | Last Updated | Age | Reason |
|-------------|--------------|-----|--------|
| Emotet API+string deobfuscator | 2020-09-21 | 5.2 years | Emotet botnet was taken down in 2021. This plugin is now obsolete. |

**Recommendation:** Remove from listing. Emotet is no longer an active threat, and the plugin has no general utility.

#### 1.2 Example/Tutorial Plugins

| Plugin Name | Last Updated | Age | Description |
|-------------|--------------|-----|-------------|
| DUMB | 2020-03-01 | 5.8 years | DUMB: An Example Architecture for Binary Ninja |
| VMNDH-2k12 Architecture Plugin | 2019-07-10 | 6.4 years | A disassembler and lifter for the VMNDH-2k12 architecture. |

**Recommendation:** These are example/tutorial plugins meant to demonstrate Binary Ninja's plugin architecture. They should either:
- Be moved to a separate "examples" category/repository
- Have clear labels indicating they're for educational purposes only
- Be removed if they no longer work with current BN versions

### Category 2: REVIEW FOR REMOVAL (31 plugins >5 years old)

These plugins haven't been updated in over 5 years and likely don't work with modern Binary Ninja versions. They should be tested and either updated or removed.

#### 2.1 Ancient Plugins (>6 years old, from 2019)

| Plugin Name | Author | Last Updated | Age | URL |
|-------------|--------|--------------|-----|-----|
| Jump table branch editor | jofra | 2019-07-06 | 6.4y | https://github.com/Vasco-jofra/jump-table-branch-editor |
| Annotate Functions | B.Kerler | 2019-07-09 | 6.4y | https://github.com/bkerler/annotate |
| MSVC | Brick | 2019-07-12 | 6.4y | https://github.com/0x1F9F1/binja-msvc |
| Sourcery Pane | mechanicalnull | 2019-07-15 | 6.4y | https://github.com/mechanicalnull/sourcery_pane |
| Format String Finder | jofra | 2019-07-15 | 6.4y | https://github.com/Vasco-jofra/format-string-finder-binja |
| Syscaller | Michal Melewski | 2019-07-15 | 6.4y | https://github.com/carstein/Syscaller |
| Windows Driver Analyzer | shareef12 | 2019-08-08 | 6.3y | https://github.com/shareef12/driveranalyzer |
| Intel 8086 Architecture | whitequark | 2019-09-04 | 6.3y | https://github.com/whitequark/binja-i8086 |
| Function ABI | whitequark | 2019-11-22 | 6.1y | https://github.com/whitequark/binja_function_abi |

**Recommendation:** These plugins are over 6 years old and have not been maintained. Binary Ninja's API has evolved significantly since 2019. These should be:
1. Tested to verify they don't work with current BN
2. Marked as deprecated or unmaintained
3. Removed from active listings if broken

#### 2.2 Old Plugins (5-6 years old, from 2020)

| Plugin Name | Author | Last Updated | Age |
|-------------|--------|--------------|-----|
| Renesas M16C Architecture | whitequark | 2020-01-19 | 5.9y |
| DUMB | toolCHAINZ | 2020-03-01 | 5.8y |
| revsync | lunixbochs | 2020-05-14 | 5.6y |
| GEF-Binja | hugsy | 2020-05-18 | 5.6y |
| Dependency analyzer | Shiz | 2020-05-25 | 5.5y |
| YARA Scan | trib0r3 | 2020-05-26 | 5.5y |
| Nampa | Paolo Montesel | 2020-05-27 | 5.5y |
| Frida | Chame1eon | 2020-06-01 | 5.5y |
| HLIL Dump | atxsinn3r | 2020-06-07 | 5.5y |
| Clean Tricks | Jan Beck | 2020-06-08 | 5.5y |
| WASM Plugin | Meador Inge | 2020-06-30 | 5.4y |
| VTIL Plugin | Layle | 2020-07-05 | 5.4y |
| Switch Loader | EliseZeroTwo | 2020-07-22 | 5.4y |
| recursion | zznop | 2020-07-22 | 5.4y |
| Emotet API+string deobfuscator | Francesco Muroni | 2020-09-21 | 5.2y |
| iBoot64 Loader | Blackwing Intelligence | 2020-10-01 | 5.2y |
| Golang Symbol Restore | Daniel Weber | 2020-10-19 | 5.1y |
| devi | @_murks | 2020-11-04 | 5.1y |
| Game Boy Loader and Architecture Plugin | Hugo Porcher | 2020-11-17 | 5.1y |
| Instruction Slicer | Andrea Ferraris | 2020-11-25 | 5.0y |
| DeGObfuscate | Jamie Hankins | 2020-12-02 | 5.0y |
| Auto Utils | 404'd | 2020-12-12 | 5.0y |
| peutils | 404'd | 2020-12-12 | 5.0y |

**Recommendation:** Test these plugins. Many might still have utility (e.g., YARA Scan, Frida integration, architecture plugins for retro systems). Decision per plugin:
- **Keep with "Unmaintained" label:** Architecture plugins for niche/retro systems (Game Boy, M16C, 8086, etc.) that might still work
- **Remove:** Utility plugins that have been superseded by better alternatives or BN built-in features
- **Seek maintainers:** Popular tools like revsync, GEF-Binja that might have community interest

### Category 3: MODERNIZATION CANDIDATES (18 plugins with Python 2 support)

These plugins still support Python 2 (deprecated since 2020) and are over 4 years old. They may still be functional but need modernization.

| Plugin Name | Last Updated | Age | Type |
|-------------|--------------|-----|------|
| Jump table branch editor | 2019-07-06 | 6.4y | core, ui |
| Annotate Functions | 2019-07-09 | 6.4y | binaryview |
| VMNDH-2k12 Architecture Plugin | 2019-07-10 | 6.4y | architecture, binaryview |
| MSVC | 2019-07-12 | 6.4y | helper |
| Sourcery Pane | 2019-07-15 | 6.4y | helper, ui |
| Windows Driver Analyzer | 2019-08-08 | 6.3y | helper |
| Intel 8086 Architecture | 2019-09-04 | 6.3y | arch |
| Function ABI | 2019-11-22 | 6.1y | ui |
| revsync | 2020-05-14 | 5.6y | ui |
| Dependency analyzer | 2020-05-25 | 5.5y | helper |
| HLIL Dump | 2020-06-07 | 5.5y | helper |
| VTIL Plugin | 2020-07-05 | 5.4y | architecture, binaryview |
| Instruction Slicer | 2020-11-25 | 5.0y | helper |

Plus 5 more from 2021-2022.

**Recommendation:** 
- **High Priority for Modernization:** Core functionality plugins like "Jump table branch editor", "MSVC", "Windows Driver Analyzer"
- **Consider Removal:** Tutorial/example plugins that still have python2
- **Community Outreach:** Contact authors to see if they're willing to update to Python 3 only

## Proposed Actions

### Immediate Actions

1. **Create a `DEPRECATED.md` file** listing all plugins in Category 1 and 2
2. **Add deprecation warnings** to `plugins.json` for plugins >5 years old
3. **Remove from active listings:**
   - Emotet API+string deobfuscator (obsolete malware family)
   - DUMB (move to examples)
   - VMNDH-2k12 (move to examples)

### Short-term Actions (1-2 weeks)

1. **Test sample plugins** from each age category to verify functionality
2. **Contact authors** of popular old plugins (revsync, GEF-Binja, Frida, etc.)
3. **Create "Unmaintained" category** in plugin listings
4. **Update README** with information about plugin maintenance status

### Long-term Actions (1-3 months)

1. **Establish maintenance criteria** for plugins
2. **Create automated checks** for:
   - Last update date
   - Python version compatibility
   - Binary Ninja version compatibility
3. **Community call for maintainers** for popular unmaintained plugins
4. **Archive repository** for dead plugins (preserve history)

## Specific Plugin Recommendations

### Plugins to KEEP (despite age)

These plugins serve niche but valid use cases and should be kept with "Unmaintained" warnings:

- **Intel 8086 Architecture** - Retro computing / DOS analysis
- **Game Boy Loader and Architecture Plugin** - Retro gaming / ROM hacking
- **Renesas M16C Architecture** - Embedded systems analysis
- **iBoot64 Loader** - iOS security research
- **Switch Loader** - Nintendo Switch reverse engineering

### Plugins to REMOVE

These have been superseded, are obsolete, or never meant for production:

- **Emotet API+string deobfuscator** - Obsolete malware family
- **DUMB** - Example plugin only
- **VMNDH-2k12 Architecture Plugin** - Example plugin only

### Plugins Needing Verification

These popular plugins should be tested to determine if they still work:

- **revsync** - Real-time IDA/BN sync (popular feature)
- **GEF-Binja** - GDB integration (popular feature)
- **Frida** - Dynamic instrumentation (popular tool)
- **YARA Scan** - Malware analysis (popular tool)
- **Nampa** - FLIRT signatures (popular feature)

## Statistics

- **Total Plugins:** 178
- **Actively Maintained (updated in last 2 years):** ~120
- **Old but Possibly Working (2-5 years):** ~22
- **Very Old (>5 years):** 31
- **Definitely Dead:** 3
- **Needs Attention:** 36 (20% of total)

## Conclusion

The Binary Ninja community plugins repository has accumulated technical debt over the years. While most plugins are well-maintained, approximately 20% require attention. A systematic approach to deprecating, removing, or modernizing these plugins will improve the user experience and reduce confusion about which plugins are currently functional.

The recommended approach is:
1. Remove obviously dead plugins immediately (Category 1)
2. Mark very old plugins as "unmaintained" with warnings
3. Reach out to community for modernization help
4. Establish ongoing maintenance criteria to prevent future accumulation

This will ensure the plugin repository remains a valuable resource for the Binary Ninja community.
