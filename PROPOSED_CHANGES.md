# Proposed Changes for Plugin Repository Cleanup

## Phase 1: Immediate Removals (Low Risk)

### Remove Example/Tutorial Plugins from Main Listing

These plugins were never meant for production use and should be removed or moved:

1. **DUMB** (toolCHAINZ)
   - Last Updated: 2020-03-01
   - Description: "DUMB: An Example Architecture for Binary Ninja"
   - **Action:** Remove from `plugins.json` or move to separate examples section
   - **Rationale:** Explicitly described as an example, 5.8 years old

2. **VMNDH-2k12 Architecture Plugin** (verylazyguy)
   - Last Updated: 2019-07-10  
   - Description: "A disassembler and lifter for the VMNDH-2k12 architecture"
   - **Action:** Remove from `plugins.json` or move to separate examples section
   - **Rationale:** Example architecture from a CTF challenge, not a real-world architecture

### Remove Obsolete Malware-Specific Plugins

3. **Emotet API+string deobfuscator** (Francesco Muroni)
   - Last Updated: 2020-09-21
   - **Action:** Remove from `plugins.json`
   - **Rationale:** Emotet botnet was taken down in January 2021. This plugin is obsolete.

## Phase 2: Create Deprecation Markers

### Add "unmaintained" Field to plugins.json Schema

Extend `plugins.json` to include a deprecation marker:

```json
{
  "name": "Plugin Name",
  "unmaintained": true,
  "unmaintainedReason": "No updates in >5 years, may not work with modern Binary Ninja"
}
```

### Mark Plugins as Unmaintained

Add the `unmaintained` flag to these plugins (>5 years old):

1. Jump table branch editor (2019-07-06)
2. Annotate Functions (2019-07-09)
3. MSVC (2019-07-12)
4. Sourcery Pane (2019-07-15)
5. Format String Finder (2019-07-15)
6. Syscaller (2019-07-15)
7. Windows Driver Analyzer (2019-08-08)
8. Intel 8086 Architecture (2019-09-04)
9. Function ABI (2019-11-22)
10. Renesas M16C Architecture (2020-01-19)
11. revsync (2020-05-14)
12. GEF-Binja (2020-05-18)
13. Dependency analyzer (2020-05-25)
14. YARA Scan (2020-05-26)
15. Nampa (2020-05-27)
16. Frida (2020-06-01)
17. HLIL Dump (2020-06-07)
18. Clean Tricks (2020-06-08)
19. WASM Plugin (2020-06-30)
20. VTIL Plugin (2020-07-05)
21. Switch Loader (2020-07-22)
22. recursion (2020-07-22)
23. iBoot64 Loader (2020-10-01)
24. Golang Symbol Restore (2020-10-19)
25. devi (2020-11-04)
26. Game Boy Loader and Architecture Plugin (2020-11-17)
27. Instruction Slicer (2020-11-25)
28. DeGObfuscate (2020-12-02)
29. Auto Utils (2020-12-12)
30. peutils (2020-12-12)

## Phase 3: Create UNMAINTAINED.md

Create a separate document listing unmaintained plugins with context:

### Architecture Plugins (May still work for niche use cases)
- Intel 8086 Architecture
- Renesas M16C Architecture  
- Game Boy Loader and Architecture Plugin
- VMNDH-2k12 Architecture Plugin (example)
- DUMB (example)

### Utility Plugins (Likely broken)
- Jump table branch editor
- Annotate Functions
- MSVC
- etc.

### Integration Plugins (May need updates)
- revsync
- GEF-Binja
- Frida
- etc.

## Phase 4: Update README.md

Add a new section to README.md:

```markdown
## Plugin Maintenance Status

The Binary Ninja community maintains a large collection of plugins. To help users find actively maintained plugins:

- 🟢 **Maintained**: Updated within the last 2 years
- 🟡 **Unmaintained**: No updates in 2-5 years, may still work
- 🔴 **Deprecated**: No updates in >5 years, likely broken
- ❌ **Obsolete**: No longer relevant (e.g., for defunct malware families)

See [UNMAINTAINED.md](UNMAINTAINED.md) for a full list of unmaintained plugins.

### Adopting an Unmaintained Plugin

If you'd like to adopt and maintain an unmaintained plugin:
1. Fork the original repository
2. Update the plugin to work with current Binary Ninja versions
3. Create a new release with updated plugin.json
4. Submit a PR to this repository updating the plugin URL

```

## Phase 5: Automated Maintenance Checks

Create a GitHub Action workflow that:

1. Checks for plugins not updated in >2 years
2. Creates issues to ask authors if plugins are still maintained
3. Automatically adds `unmaintained: true` flag after 5 years
4. Generates a report of plugin health

## Implementation Priority

### High Priority (Do First)
1. ✅ Remove example plugins (DUMB, VMNDH-2k12)
2. ✅ Remove obsolete plugins (Emotet deobfuscator)
3. ✅ Create PLUGIN_ANALYSIS.md (documentation)
4. ✅ Create PROPOSED_CHANGES.md (this document)

### Medium Priority (Do Soon)
5. ⏳ Add `unmaintained` field to plugins.json schema
6. ⏳ Mark 30 very old plugins as unmaintained
7. ⏳ Create UNMAINTAINED.md
8. ⏳ Update README.md with maintenance status section

### Low Priority (Nice to Have)
9. ⏳ Create GitHub Action for automated checks
10. ⏳ Contact authors of popular unmaintained plugins
11. ⏳ Test sample plugins to verify functionality
12. ⏳ Create community call for plugin adopters

## Risk Assessment

### Low Risk Changes (Can do immediately)
- Remove example plugins (DUMB, VMNDH-2k12)
- Remove obsolete plugins (Emotet)
- Add documentation files

### Medium Risk Changes (Need validation)
- Mark plugins as unmaintained
- Create separate unmaintained listing
- Update README

### High Risk Changes (Need careful consideration)
- Removing plugins that might still work
- Changing plugin.json schema (may break tools)
- Contacting plugin authors

## Success Metrics

After implementation, we should see:
- ✅ Clearer documentation about plugin maintenance status
- ✅ Reduced confusion for users trying old plugins
- ✅ Easy path for community members to adopt unmaintained plugins
- ✅ Automated processes to prevent future accumulation of dead plugins
- ✅ Better user experience in the plugin manager

## Next Steps

1. Review this proposal with maintainers
2. Get approval for Phase 1 changes (immediate removals)
3. Implement changes incrementally
4. Monitor community feedback
5. Adjust approach based on feedback

## Questions to Answer

Before implementing, we need to decide:

1. **Should we remove plugins or just mark them?**
   - Option A: Remove dead plugins entirely
   - Option B: Keep them but mark as unmaintained
   - **Recommendation:** Option B for most, Option A for examples/obsolete

2. **How do we handle the plugin.json schema change?**
   - Need to ensure backward compatibility
   - Coordinate with Binary Ninja plugin manager

3. **Should we contact plugin authors first?**
   - Pro: Gives them a chance to update
   - Con: Delays cleanup, many authors may be unreachable
   - **Recommendation:** Contact authors of popular plugins only

4. **What defines "unmaintained"?**
   - **Current proposal:** No updates in >5 years
   - Alternative: >3 years, or >2 years + binary ninja version compatibility

5. **Should we create a separate "legacy" repository?**
   - Pro: Preserves history, cleaner main repo
   - Con: More maintenance, split community
   - **Recommendation:** No, just use tags/flags in existing repo
