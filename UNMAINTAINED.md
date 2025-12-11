# Unmaintained Plugins

This document lists Binary Ninja community plugins that haven't been updated in over 5 years. These plugins may not work with current versions of Binary Ninja, though some (particularly architecture plugins for retro/embedded systems) might still be functional for specific use cases.

**Last Updated:** 2025-12-11  
**Total Unmaintained Plugins:** 28

## ⚠️ Important Notes

- **"Unmaintained" does not mean "broken"** - Some plugins may still work perfectly
- **Test before using** - Verify compatibility with your Binary Ninja version
- **Consider adopting** - If you find a plugin useful, consider maintaining it
- **Niche architectures** - Architecture plugins for retro/embedded systems are less likely to break

## Plugins by Category

### Architecture Plugins (May still work for niche use cases)

These plugins add support for specific architectures and may still work since architecture support is relatively stable:

| Plugin | Author | Last Updated | Description |
|--------|--------|--------------|-------------|
| [Intel 8086 Architecture](https://github.com/whitequark/binja-i8086) | whitequark | 2019-09-04 | 16-bit Intel architecture (DOS, retro computing) |
| [Renesas M16C Architecture](https://github.com/whitequark/binja-m16c) | whitequark | 2020-01-19 | Renesas M16C (embedded systems) |
| [Game Boy Loader and Architecture Plugin](https://github.com/icecr4ck/bnGB) | Hugo Porcher | 2020-11-17 | Game Boy ROM analysis |
| [WASM Plugin](https://github.com/ivision-research/binjawa) | Meador Inge | 2020-06-30 | WebAssembly disassembly and lifting |
| [VTIL Plugin](https://github.com/vtil-project/VTIL-BinaryNinja) | Layle | 2020-07-05 | Virtual-machine Translation Intermediate Language |

**Status:** Worth trying if you need these specific architectures. They target stable platforms and may still work.

### Binary Format Loaders

These plugins load specific binary formats:

| Plugin | Author | Last Updated | Description |
|--------|--------|--------------|-------------|
| [iBoot64 Loader](https://github.com/BlackwingHQ/iBoot64Binja) | Blackwing Intelligence | 2020-10-01 | iOS iBoot/SecureROM firmware |
| [Switch Loader](https://github.com/EliseZeroTwo/Switch-Binja-Loader) | EliseZeroTwo | 2020-07-22 | Nintendo Switch binaries |
| [GameCube DOL](https://github.com/PistonMiner/binaryninja-gc-dol) | Linus S. | 2021-07-08 | GameCube DOL files |
| [DBG Loader](https://github.com/gamozolabs/coff_nm) | Gamozo Labs | 2021-11-15 | Old COFF .dbg files |

**Status:** May work for specialized use cases. Test with your specific binary format.

### Analysis & Helper Tools

These plugins add analysis capabilities or helper functionality:

| Plugin | Author | Last Updated | Description |
|--------|--------|--------------|-------------|
| [Jump table branch editor](https://github.com/Vasco-jofra/jump-table-branch-editor) | jofra | 2019-07-06 | Fix jump table branches |
| [Annotate Functions](https://github.com/bkerler/annotate) | B.Kerler | 2019-07-09 | Annotate function arguments |
| [MSVC](https://github.com/0x1F9F1/binja-msvc) | Brick | 2019-07-12 | Parse MSVC structures |
| [Format String Finder](https://github.com/Vasco-jofra/format-string-finder-binja) | jofra | 2019-07-15 | Find format string vulnerabilities |
| [Syscaller](https://github.com/carstein/Syscaller) | Michal Melewski | 2019-07-15 | Decorate syscalls with details |
| [Windows Driver Analyzer](https://github.com/shareef12/driveranalyzer) | shareef12 | 2019-08-08 | Find IRP dispatch routines |
| [Dependency analyzer](https://github.com/shizmob/binja-depanalyzer) | Shiz | 2020-05-25 | Analyze dependencies |
| [YARA Scan](https://github.com/trib0r3/binja-yara) | trib0r3 | 2020-05-26 | YARA signatures |
| [Nampa](https://github.com/thebabush/nampa) | Paolo Montesel | 2020-05-27 | FLIRT for Binary Ninja |
| [HLIL Dump](https://github.com/atxsinn3r/BinjaHLILDump) | atxsinn3r | 2020-06-07 | Dump HLIL to directory |
| [Clean Tricks](https://github.com/janbbeck/CleanTricks) | Jan Beck | 2020-06-08 | Remove simple obfuscation |
| [recursion](https://github.com/zznop/bn-recursion) | zznop | 2020-07-22 | Locate and annotate recursion |
| [Golang Symbol Restore](https://github.com/d-we/binja-golang-symbol-restore) | Daniel Weber | 2020-10-19 | Restore Go function names |
| [devi](https://github.com/murx-/devi_binja) | @_murks | 2020-11-04 | Devirtualize C++ virtual calls |
| [Instruction Slicer](https://github.com/c3r34lk1ll3r/Instruction_Slicer) | Andrea Ferraris | 2020-11-25 | Forward/backward slicing |
| [DeGObfuscate](https://github.com/kryptoslogic/binja_degobfuscate) | Jamie Hankins | 2020-12-02 | De-obfuscate Go strings |
| [Auto Utils](https://github.com/404d/autoutils) | 404'd | 2020-12-12 | Auto analysis utilities |
| [peutils](https://github.com/404d/peutils) | 404'd | 2020-12-12 | PE binary utilities |
| [Binary Ninja Type Manager](https://github.com/Ayrx/binja-typemanager) | Terry Chia | 2021-01-30 | Manage type libraries |
| [GO Loader Assist](https://github.com/f0rki/bn-goloader) | Michael Rodler | 2021-02-02 | Parse Go symbol table |
| [GameCube symbol map loader](https://github.com/PistonMiner/binaryninja-gc-load-map) | Linus S. | 2021-07-08 | Load GameCube symbols |

**Status:** Likely broken with modern Binary Ninja due to API changes. High risk of incompatibility.

### Integration & UI Plugins

These plugins integrate with external tools or modify the UI:

| Plugin | Author | Last Updated | Description |
|--------|--------|--------------|-------------|
| [Sourcery Pane](https://github.com/mechanicalnull/sourcery_pane) | mechanicalnull | 2019-07-15 | Synchronized source code pane |
| [Function ABI](https://github.com/whitequark/binja_function_abi) | whitequark | 2019-11-22 | GUI for changing function ABI |
| [revsync](https://github.com/lunixbochs/revsync) | lunixbochs | 2020-05-14 | Realtime IDA/BN sync |
| [GEF-Binja](https://github.com/hugsy/gef-binja) | hugsy | 2020-05-18 | Interface with GDB-GEF |
| [Frida](https://github.com/chame1eon/binaryninja-frida) | Chame1eon | 2020-06-01 | Frida integration |

**Status:** High risk of incompatibility. External tool integrations often break with updates.

## How to Adopt an Unmaintained Plugin

If you find an unmaintained plugin useful and want to update it:

1. **Test it first** - Verify if it still works or what needs fixing
2. **Fork the repository** - Create your own copy on GitHub
3. **Update for compatibility** - Fix any API compatibility issues
4. **Update plugin.json** - Ensure minimumBinaryNinjaVersion is correct
5. **Create a release** - Tag and release your updated version
6. **Submit a PR** - Update this repository's plugins.json with your new URL

### Resources for Plugin Developers

- [Binary Ninja API Documentation](https://api.binary.ninja/)
- [Plugin Development Guide](https://docs.binary.ninja/dev/plugins.html)
- [Sample Plugin Template](https://github.com/Vector35/sample_plugin)
- [Official Example Plugins](https://github.com/Vector35/binaryninja-api/tree/dev/python/examples)

## Recently Removed Plugins

The following plugins were removed from the repository (not just marked unmaintained):

### Removed 2025-12-11

1. **DUMB** - Example architecture plugin, not meant for production use
2. **VMNDH-2k12 Architecture Plugin** - Example CTF architecture, not a real architecture
3. **Emotet API+string deobfuscator** - Malware family taken down in 2021, no longer relevant

See [PROPOSED_CHANGES.md](PROPOSED_CHANGES.md) for the complete rationale.

## Reporting Status

If you've tested an unmaintained plugin:

- **Still works?** Please let us know by opening an issue! We can update this document.
- **Broken?** Document what's broken to help future maintainers.
- **Updated it?** Submit a PR to update plugins.json with your maintained version.

## Statistics

As of 2025-12-11:

- Total plugins: 175
- Plugins <2 years old: 84 (48%)
- Plugins 2-5 years old: 63 (36%)
- **Plugins >5 years old: 28 (16%)** ← You are here

---

*This document is maintained as part of the Binary Ninja community plugins repository. For more information about plugin maintenance, see [PLUGIN_ANALYSIS.md](PLUGIN_ANALYSIS.md).*
