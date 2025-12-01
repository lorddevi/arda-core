# AI Agent Instructions

## Work Tracking

- Use the 'bd' tool for all issue tracking - NO markdown TODOs
- Every task, bug, and feature must be filed as a beads issue
- Always include detailed context in issue descriptions

### Rich Context Files (Optional)

For complex work, create detailed context files to improve discoverability and provide complete context for future developers or AI agents.

**Process:**

1. **Create Issue**

   ```bash
   bd create --title="..." --type=task|bug|feature
   ```

2. **Create Context File** (optional but recommended for complex work)

   **Option A: Using helper script (recommended)**

   ```bash
   .beads/create-context.sh beads-XXX task
   # Edit the generated file and fill in all {placeholders}
   ```

   **Option B: Manual template copy**

   ```bash
   # Copy appropriate template
   cp .beads/templates/task.md .beads/context/{issue-id}.md
   cp .beads/templates/bug.md .beads/context/{issue-id}.md
   cp .beads/templates/feature.md .beads/context/{issue-id}.md

   # Fill in the template
   # - Replace {id}, {title}, {status}
   # - Complete User Story section
   # - List Acceptance Criteria with [ ]
   # - Add Tasks/Subtasks with [ ]
   # - Include Architecture Notes
   # - Add References to code/docs
   ```

3. **Update as Work Progresses**

   ```bash
   # Edit .beads/context/{issue-id}.md
   # Mark completed tasks: - [x] Task
   # Add implementation log entries with dates
   # Document changes in Files Changed section
   # Commit context file with code changes
   ```

4. **Benefits**
   - Anyone can read the context file to understand the full story
   - References to code/docs make it easy to find related work
   - Architecture notes preserve important decisions
   - Implementation log shows how work evolved
   - Files changed section documents impact

**Templates available:**

- `.beads/templates/task.md` - For tasks and fixes
- `.beads/templates/bug.md` - For bug reports and fixes
- `.beads/templates/feature.md` - For new features

**Example:**

```markdown
# Issue beads-59o: Fix test pollution in arda-cli

Status: closed

## User Story

As a developer working on arda-cli,
I want tests to run in isolation without pollution from other tests,
So that I can trust test results and not have flaky test failures.

## Acceptance Criteria

- [x] Each test starts with clean module state
- [x] Config state is reset between tests
- [x] Test pollution no longer causes failures
- [x] All tests pass consistently

## Tasks

- [x] Identify sources of test pollution
- [x] Implement reset_modules() fixture
- [x] Add clean_config_state() autouse fixture

## Architecture Notes

**Root Cause:** Module-level config cache in main.py computed at import time...

## References

- [Code: pkgs/arda-cli/arda_cli/main.py](pkgs/arda-cli/arda_cli/main.py)
- [Tests: pkgs/arda-cli/arda_cli/tests/conftest.py](pkgs/arda-cli/arda_cli/tests/conftest.py)
```

## MCP Usage

### mcp 'Ref' - Official Documentation Lookup

**Use for:** API references, official documentation, library guides

**Best for:**

- Looking up React hooks, Python libraries, AWS SDKs
- Finding official API documentation
- Checking package references and usage patterns
- arda-core repository reference (search: "lorddevi/arda-core")

**Tools available:**

- `ref_search_documentation` - Find documentation for libraries/frameworks
- `ref_read_url` - Read specific documentation pages

**When to use:**

- ✅ You know the exact library/framework name
- ✅ You need authoritative API information
- ✅ Checking if a feature exists in official docs
- ✅ Looking up specific function/class signatures

**When NOT to use:**

- ❌ Niche or newer libraries (not indexed)
- ❌ Community tutorials or examples (use Exa instead)
- ❌ GitHub repositories (use Exa instead)
- ❌ Stack Overflow questions (use Exa instead)

**Context efficiency:** Minimal - returns focused documentation

### mcp 'exa' - Web Search & Code Research

**Use for:** Everything not covered by Ref - research, examples, tutorials, repositories

**Best for:**

- Finding code examples and tutorials
- Researching new libraries or tools
- GitHub repositories (like beads, niche projects)
- Stack Overflow answers and discussions
- Blog posts and community guides
- NixOS-specific research (arda-core is a NixOS orchestration system!)

**Tools available:**

- `exa web_search_exa` - Search the web with configurable depth (fast/auto/deep)
- `exa get_code_context_exa` - Get code examples with controllable token limits (1000-50000)

**When to use:**

- ✅ Researching how to use a library
- ✅ Finding GitHub repositories
- ✅ Stack Overflow, Reddit, forums
- ✅ NixOS packages, configurations, home-manager settings
- ✅ Community tutorials and blog posts
- ✅ Understanding implementation patterns
- ✅ Verifying examples work in practice

**When NOT to use:**

- ❌ Official API reference (use Ref instead for cleaner context)

**Context efficiency:** Controllable via `tokensNum` parameter

- Low context: `tokensNum=1000-2000` (quick lookup)
- Balanced: `tokensNum=3000-5000` (typical research)
- Deep dive: `tokensNum=5000+` (complex topics)

### mcp 'nixos' - Comprehensive Nix Ecosystem

**Use for:** Complete NixOS ecosystem - packages, options, version history, Home Manager, nix-darwin, flakes

**Note:** No Nix/NixOS installation required! Works on Windows, macOS, Linux.

#### 🔍 Core NixOS Tools (130K+ packages, 22K+ options)

**Best for:**

- Finding NixOS packages (`nixos_search`)
- Looking up configuration options (`nixos_info`)
- Package/option statistics (`nixos_stats`)
- Available channels (`nixos_channels`)

**Tools:**

- `nixos_search(query, type, channel)` - Search packages, options, or programs
- `nixos_info(name, type, channel)` - Get detailed info about packages/options
- `nixos_stats(channel)` - Package and option counts
- `nixos_channels()` - List all available channels

**When to use:**

- ✅ Finding packages for NixOS configurations
- ✅ Looking up option documentation (services, programs, etc.)
- ✅ Checking what's available in specific channels

#### 📦 Version History Tools (via NixHub.io)

**Best for:**

- Package version tracking with commit hashes
- Finding specific versions for reproducible builds
- Historical dependency analysis

**Tools:**

- `nixhub_package_versions(package, limit)` - Get version history with commit hashes
- `nixhub_find_version(package, version)` - Smart search for specific versions

**When to use:**

- ✅ Pinning specific package versions
- ✅ Finding historical versions for debugging
- ✅ Reproducible builds with exact commit references

#### 🏠 Home Manager Tools (4K+ options, 131 categories)

**Best for:**

- User configuration options
- Home directory management
- Dotfiles and user services

**Tools:**

- `home_manager_search(query)` - Search user config options
- `home_manager_info(name)` - Get option details (with suggestions!)
- `home_manager_stats()` - See what's available
- `home_manager_list_options()` - Browse all 131 categories
- `home_manager_options_by_prefix(prefix)` - Explore options by prefix

**When to use:**

- ✅ User configuration (home.manager, git, ssh, etc.)
- ✅ Dotfiles management
- ✅ User-level services

#### 🍎 nix-darwin Tools (1K+ options, 21 categories)

**Best for:**

- macOS system configuration via Nix
- Darwin-specific options

**Tools:**

- `darwin_search(query)` - Search macOS options
- `darwin_info(name)` - Get option details
- `darwin_stats()` - macOS configuration statistics
- `darwin_list_options()` - Browse all 21 categories
- `darwin_options_by_prefix(prefix)` - Explore macOS options

**When to use:**

- ✅ macOS system configuration
- ✅ Darwin-specific services and settings

#### 🔥 Flake Search

**Best for:**

- Community packages and templates

**Tools:**

- `nixos_flakes_search(query)` - Search community flakes
- `nixos_flakes_stats()` - Flake ecosystem statistics

**When to use:**

- ✅ Finding community flakes
- ✅ Templates and shared configurations
- ✅ External Nix resources

**When to use NixOS MCP:**

- ✅ Any NixOS-related work (arda-core is a NixOS orchestration system!)
- ✅ Finding packages to include in NixOS configurations
- ✅ Looking up configuration option details for NixOS, Home Manager, or nix-darwin
- ✅ Checking package availability and versions
- ✅ Version history and commit tracking for reproducibility
- ✅ Exploring flake community resources

### mcp 'jump' - Justfile Integration

**Use for:** Just commands and automation

**Tools:**

- `jump list_recipes` - Show available commands
- `jump get_recipe_info` - Get details on specific commands
- `jump run_recipe` - Execute Just commands

**When to use:**

- ✅ Checking what commands are available in the Justfile
- ✅ Understanding what a specific command does
- ✅ Running automation tasks

### Research Workflow for arda-core (NixOS Orchestration)

Given arda-core's niche nature as a NixOS orchestration system:

1. **Start with Ref** for known frameworks (React, Python, etc.)
2. **Use Exa liberally** for NixOS-specific research
3. **Use NixOS MCP** for package/option lookups
4. **Use Jump MCP** for project-specific commands

**Example:**

```bash
## Research NixOS service configuration for a feature
exa get_code_context_exa --query "nixos service configuration systemd examples" --tokensNum 3000

## Find and explore NixOS packages
nixos_search --query "ssh configuration"
nixos_info --name "openssh" --type "package"
nixos_channels

## Check Home Manager options for user configs
home_manager_search --query "git"
home_manager_info --name "programs.git.enable"

## Find specific package versions for reproducibility
nixhub_package_versions --package_name "python" --limit 10
nixhub_find_version --package_name "ruby" --version "2.6.7"

## Search community flakes
nixos_flakes_search --query "arda"
exa web_search_exa --query "arda-core nix orchestration patterns" --type deep
```

## 🔄 Beads Sync Workflow

Beads uses **git worktrees** to manage issues. Understanding when to sync is critical.

### How It Works

Beads creates a **separate worktree** (`beads-sync`) that shares your git database but:

- Has **ONLY** `.beads/` directory files
- Can be synced independently from your main code
- Maintains its own git branch and history

### When to Use Each Command

#### **`bd sync`** - Normal Bidirectional Sync

**Use for:**

- ✅ Long-lived branches (testing-phase-13, master, main, feature branches you keep)
- ✅ Regular development work
- ✅ Day-to-day issue management

**What it does:**

- Syncs between your current branch and the beads-sync worktree
- **Bidirectional**: changes flow both ways
- Export issues from SQLite to JSONL
- Commit bead changes to beads-sync branch
- Push/pull bead changes to remote

**Workflow:**

```bash
## On testing-phase-13 (or any long-lived branch)
bd create "New issue"          # Create issues
bd close <id>                  # Close issues
bd update <id> --status in_progress  # Update status

## Sync your changes to beads-sync worktree
bd sync                         # ✓ Bidirectional sync

## Commit and push
git add .beads && git commit -m "Update beads"
git push
```

#### **`bd sync --from-main`** - One-Way from Main Branch

**Use for:**

- ✅ **Ephemeral branches** (short-lived feature branches)
- ✅ Branches that **don't have bead history** yet
- ✅ Pulling bead state from main into a new branch

**What it does:**

- **One-way sync**: Pulls bead state FROM main INTO your branch
- Does NOT sync changes back to main
- Designed for ephemeral branches without upstream tracking

**Workflow:**

```bash
## Create new ephemeral branch
git checkout -b feature-x

## First time: pull bead state FROM main
bd sync --from-main             # ✓ One-way pull from main

## Work on feature
bd create "Work on feature-x"   # Create issues
bd sync                         # Normal sync for ongoing work

## Before merging back
bd sync                         # Final sync
git checkout testing-phase-13
git merge feature-x
```

### Decision Tree

```
Are you on a long-lived branch? (testing-phase-13, master, feature branch you keep)
├─ YES → Use: bd sync
└─ NO (ephemeral feature branch)?
    └─ First time on this branch?
        ├─ YES → Use: bd sync --from-main
        └─ NO → Use: bd sync
```

### Other Useful Flags

```bash
## Check sync status without syncing
bd sync --status

## After git pull on main branch
bd sync --import-only    # Just import JSONL changes

## Preview sync without changes
bd sync --dry-run
```

### For arda-core Project

**Current branch: testing-phase-13** → Use: `bd sync` (long-lived branch)
**New feature branches** → Use: `bd sync --from-main` (first time only)

### Common Mistakes

❌ **Wrong**: Using `--from-main` on long-lived branches

```bash
## DON'T do this on testing-phase-13!
bd sync --from-main  # Tries to overwrite with main's bead state
```

✅ **Correct**: Using normal sync on long-lived branches

```bash
## DO this on testing-phase-13
bd sync  # Bidirectional sync with beads-sync worktree
```

## 🚨 SESSION CLOSE PROTOCOL 🚨

**CRITICAL**: Before saying "done" or "complete", you MUST run this checklist:

```
[ ] 1. git status              (check what changed)
[ ] 2. git add <files>         (stage code changes)
[ ] 3. bd sync                 (sync beads with beads-sync worktree)
[ ] 4. git commit -m "..."     (commit code changes)
[ ] 5. git pull --rebase       (pull latest from remote)
[ ] 6. bd sync                 (sync again after pull)
[ ] 7. git push                (PUSH TO REMOTE - MANDATORY)
[ ] 8. git status              (verify clean state)
```

**The plane has NOT landed until `git push` succeeds.**

## Core Rules

- Track ALL work in beads (no TodoWrite tool, no markdown TODOs)
- Use `bd create` to create issues, not TodoWrite tool
- Git workflow: hooks auto-sync, run `bd sync` at session end
- Session management: check `bd ready` for available work

## Essential Commands

### Finding Work

- `bd ready` - Show issues ready to work (no blockers)
- `bd list --status=open` - All open issues
- `bd list --status=in_progress` - Your active work
- `bd show <id>` - Detailed issue view with dependencies

### Creating & Updating

- `bd create --title="..." --type=task|bug|feature` - New issue
- `bd update <id> --status=in_progress` - Claim work
- `bd update <id> --assignee=username` - Assign to someone
- `bd close <id>` - Mark complete
- `bd close <id> --reason="explanation"` - Close with reason

### Dependencies & Blocking

- `bd dep add <issue> <depends-on>` - Add dependency (issue depends on depends-on)
- `bd blocked` - Show all blocked issues
- `bd show <id>` - See what's blocking/blocked by this issue

### Sync & Collaboration

- `bd sync --from-main` - Pull beads updates from main (for ephemeral branches)
- `bd sync --status` - Check sync status without syncing

### Project Health

- `bd stats` - Project statistics (open/closed/blocked counts)
- `bd doctor` - Check for issues (sync problems, missing hooks)

## Common Workflows

**Starting work:**

```bash
bd ready           # Find available work
bd show <id>       # Review issue details
bd update <id> --status in_progress  # Claim it
```

**Completing work:**

```bash
bd close <id>           # Mark done
bd sync --from-main     # Pull latest beads from main
git add . && git commit -m "..."  # Commit your changes
## Merge to main when ready (local merge, not push)
```

**Creating dependent work:**

```bash
bd create --title="Implement feature X" --type=feature
bd create --title="Write tests for X" --type=task
bd dep add beads-yyy beads-xxx  # Tests depend on Feature (Feature blocks tests)
```
