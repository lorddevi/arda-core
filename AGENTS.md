# MCP Usage Policies

This project has several MCP servers configured to enhance AI-assisted development. Each server serves a specific purpose:

## 1. Documentation vs. Research (The "Ref vs. Exa" Rule)

* **mcp__Ref__ (Official Docs):**
  * **TRIGGER:** Use this FIRST when you need authoritative syntax, API signatures, or standard library usage for known frameworks (React, Python, AWS).
  * **CONSTRAINT:** Do NOT use for niche libraries, tutorials, or debugging discussions.
* **mcp__exa__ (Web/Research):**
  * **TRIGGER:** Use this for **NixOS research**, community tutorials, finding new GitHub repos, or specific error debugging.
  * **TOKEN GUIDE:**
    * Use `tokensNum="dynamic"` (recommended) - automatically adjusts token usage for optimal results.

## 2. NixOS Ecosystem (mcp__nixos__)

* **Scope:** This server is the **Source of Truth** for all things Nix. It covers NixOS, Home Manager, Darwin, and Flakes.
* **CRITICAL RULE:** Do not hallucinate package names. **Always** use `nixos_search` or `home_manager_search` to verify a package exists before suggesting it in code.
* **Version Pinning:** If reproducibility is required, you must use `nixhub_package_versions` to find the exact commit hash.
* **Context:** `arda-core` is an orchestration system; prefer NixOS-native solutions found here over generic Linux solutions found via web search.

## 3. Project Automation (mcp__just__)

* **Usage:** Use this to explore and execute the project's `Justfile`.
* **Workflow:** Before suggesting a user run a manual terminal command, check `mcp__just__help()` to see what automation shortcuts already exist.

## 4. Issue Tracking (mcp__beads__)

* **Usage:** For creating, updating, and managing project issues. Alternative to CLI `bd` commands.
* **Workflow:** See "Issue Tracking with bd (beads)" section below for detailed usage patterns.
* **Note:** The MCP interface provides the same functionality as `bd` CLI commands - use whichever is convenient for your workflow.

## 5. Semantic Code Search (mgrep)

* **Usage:** Use this for natural-language code search and codebase exploration. mgrep understands intent and meaning, not just exact string matches.
* **WHEN TO USE:**
  * Exploring unfamiliar codebases - find functionality by describing what you want, not what it's called
  * Discovering features or implementations across large repositories
  * Semantic code search when grep's exact matching isn't finding what you need
  * Enhancing AI agent workflows with intent-based code discovery
* **CONSTRAINT:** Complement, don't replace traditional grep - use grep for exact matches, regex, and symbol tracing
* **Note:** Requires authentication via Mixedbread account. Run `mgrep login` or configure API key for full functionality

## 6. IDE-Like Code Analysis & Editing (Serena)

* **Scope:** Serena transforms you into an IDE-capable agent with semantic code understanding and precise editing abilities. It uses Language Server Protocol (LSP) for symbol-level code operations across 30+ languages.
* **TRIGGER:** Use Serena FIRST for any code analysis or editing task, especially:
  * **Understanding code relationships** - Find references, callers, dependencies with `find_referencing_symbols()`
  * **Targeted reading** - Get symbol overviews with `get_symbols_overview()` before reading files
  * **Precise edits** - Replace specific function/class bodies with `replace_symbol_body()`
  * **Symbol operations** - Rename, insert before/after specific symbols with LSP accuracy
  * **Large codebases** - Navigate complex projects without reading entire files (massive token savings!)
* **CONSTRAINT:**
  * Only useful for code that exists - not for writing from scratch
  * Minimal benefit on tiny files or simple tasks
  * Still use `grep`/`find` for regex patterns or when you need exact string matching
* **TOKEN EFFICIENCY:** Serena can reduce token usage by 80-90% compared to reading entire files. Always try symbolic operations first.
* **CRITICAL WORKFLOW:**
  1. **Check onboarding**: `check_onboarding_performed()` - Run this before working on any new project!
  2. **Symbol search**: Find what you need with `find_symbol()` before reading files
  3. **Understand relationships**: Use `find_referencing_symbols()` to see full context
  4. **Think before editing**: Use `think_about_collected_information()` to verify understanding
  5. **Make precise edits**: Use symbol-based editing tools, never string replacement
* **POWER TOOLS:**
  * `read_memory()` / `write_memory()` - Persist important project knowledge
  * `replace_symbol_body()` - Perfect for refactoring functions/classes
  * `rename_symbol()` - Safe refactoring with LSP guarantees

## Recommended Research Workflow

1. **Analyze Codebase:** Use `mcp__serena__*` tools for semantic code understanding, symbol search, and precise editing (80-90% token savings!). Run `mcp__serena__check_onboarding_performed()` first for new projects.
2. **Check Internal:** Use `mcp__just__help()` to see if a task is already automated.
3. **Check Codebase:** Use `mcp__mgrep__*` for semantic search across the local codebase when exploring unfamiliar code or finding implementation details.
4. **Check Official:** Use `mcp__Ref__*` if standard library syntax is needed.
5. **Check Nix:** Use `mcp__nixos__*` to verify package availability/options.
6. **Check External:** Use `mcp__exa__*` (deep mode) for architectural research or error hunting.

## Example Usage

**Quick fact check:**

```
mcp__exa__web_search_exa(query="python async await best practices", numResults=5, tokensNum=1000)
```

**Verify package availability:**

```
mcp__nixos__nixos_search(query="python311", search_type="packages")
```

**Check project automation:**

```
mcp__just__help()
```

**Get official documentation:**

```
mcp__Ref__ref_search_documentation(query="React useState hook TypeScript")
```

## Issue Tracking with bd (beads)

**IMPORTANT**: This project uses **bd (beads)** for ALL issue tracking. Do NOT use markdown TODOs, task lists, or other tracking methods.

## Why bd?

* Dependency-aware: Track blockers and relationships between issues
* Git-friendly: Auto-syncs to JSONL for version control
* Agent-optimized: JSON output, ready work detection, discovered-from links
* Prevents duplicate tracking systems and confusion

## Quick Start

**Check for ready work:**

```bash
bd ready --json
```

**Create new issues:**

```bash
bd create "Issue title" -t bug|feature|task -p 0-4 --json
bd create "Issue title" -p 1 --deps discovered-from:bd-123 --json
bd create "Subtask" --parent <epic-id> --json  # Hierarchical subtask (gets ID like epic-id.1)
```

**Claim and update:**

```bash
bd update bd-42 --status in_progress --json
bd update bd-42 --priority 1 --json
```

**Complete work:**

```bash
bd close bd-42 --reason "Completed" --json
```

## Issue Types

* `bug` - Something broken
* `feature` - New functionality
* `task` - Work item (tests, docs, refactoring)
* `epic` - Large feature with subtasks
* `chore` - Maintenance (dependencies, tooling)

## Priorities

* `0` - Critical (security, data loss, broken builds)
* `1` - High (major features, important bugs)
* `2` - Medium (default, nice-to-have)
* `3` - Low (polish, optimization)
* `4` - Backlog (future ideas)

## Workflow for AI Agents

1. **Check ready work**: `bd ready` shows unblocked issues
2. **Claim your task**: `bd update <id> --status in_progress`
3. **Work on it**: Implement, test, document
4. **Discover new work?** Create linked issue:
   * `bd create "Found bug" -p 1 --deps discovered-from:<parent-id>`
5. **Complete**: `bd close <id> --reason "Done"`
6. **Commit together**: Always commit the `.beads/issues.jsonl` file together with the code changes so issue state stays in sync with code state

## Auto-Sync

bd automatically syncs with git:

* Exports to `.beads/issues.jsonl` after changes (5s debounce)
* Imports from JSONL when newer (e.g., after `git pull`)
* No manual export/import needed!

## MCP Server (Recommended)

Use `mcp__beads__*` functions instead of CLI commands.

## Managing AI-Generated Planning Documents

AI assistants often create planning and design documents during development:

* PLAN.md, IMPLEMENTATION.md, ARCHITECTURE.md
* DESIGN.md, CODEBASE_SUMMARY.md, INTEGRATION_PLAN.md
* TESTING_GUIDE.md, TECHNICAL_DESIGN.md, and similar files

### Best Practice: Use a dedicated directory for these ephemeral files

**Recommended approach:**

* Create a `history/` directory in the project root
* Store ALL AI-generated planning/design docs in `history/`
* Keep the repository root clean and focused on permanent project files
* Only access `history/` when explicitly asked to review past planning

**Example .gitignore entry (optional):**

```
# AI planning documents (ephemeral)
history/
```

**Benefits:**

* ✅ Clean repository root
* ✅ Clear separation between ephemeral and permanent documentation
* ✅ Easy to exclude from version control if desired
* ✅ Preserves planning history for archeological research
* ✅ Reduces noise when browsing the project

## CLI Help

Run `bd <command> --help` to see all available flags for any command.
For example: `bd create --help` shows `--parent`, `--deps`, `--assignee`, etc.

## Important Rules

* ✅ Use bd for ALL task tracking
* ✅ Always use `--json` flag for programmatic use
* ✅ Link discovered work with `discovered-from` dependencies
* ✅ Check `bd ready` before asking "what should I work on?"
* ✅ Store AI planning docs in `history/` directory
* ✅ Run `bd <cmd> --help` to discover available flags
* ❌ Do NOT create markdown TODO lists
* ❌ Do NOT use external issue trackers
* ❌ Do NOT duplicate tracking systems
* ❌ Do NOT clutter repo root with planning documents

For more details, see README.md and QUICKSTART.md.

## Agent Coding Guidelines for Arda

## Build/Test Commands

* **Single test**: `pytest pkgs/arda-cli/arda_cli/tests/unit/commands/test_<module>.py::test_<name>` (add `-v` for verbose)
* **Phase 1 tests** (fast, isolated): `just test-without-core`
* **Phase 2 tests** (with core): `just test-with-core`
* **All pytest tests**: `just test-two-phase`
* **CLI VM tests**: `just test-vm-cli`
* **Coverage report**: `just coverage`
* **Build CLI**: `just build-arda-cli`
* **Full test suite**: `just test-all`

## Code Style

* **Linting/Formatting**: Use `ruff` (configured in pyproject.toml) - `ruff check . && ruff format .`
* **Type checking**: `mypy` with strict settings (disallow_untyped_defs=true)
* **Line length**: 88 characters (Black-compatible)
* **Python version**: >=3.11, target py311
* **Formatting**: Double quotes, space indentation, comma preservation
* **Security**: `bandit` for security linting (excludes tests)

## Python Conventions

* **Framework**: Click + rich-click for CLI, Pydantic for config
* **Type hints**: Required everywhere (strict MyPy)
* **Imports**: Use absolute imports, group by standard library/third-party/local
* **Naming**: snake_case functions/variables, PascalCase classes
* **Error handling**: Use Pydantic validation, rich error panels for CLI
* **Tests**: Use pytest markers (fast, slow, unit, integration, cli, vm, with_core, without_core)

## Development Workflow

* **Issue tracking**: Use `bd` (beads) commands, never TodoWrite tool
* **Session end**: Run `bd sync && git add . && git commit -m "..." && git push`
* **Pre-commit**: Runs automatically (ruff, treefmt, build, pytest)
* **Nix environment**: Use `nix develop` for all development

## Critical Rules

* Tests run in isolation - module state is reset between tests
* Use existing patterns from codebase (rich-click theming, Pydantic config)
* Never commit secrets (detected by pre-commit hooks)
* Follow the Service/Feature/Role hierarchy for NixOS modules
