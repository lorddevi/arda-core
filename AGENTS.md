# AI Agent Instructions

## Work Tracking
- Use the 'bd' tool for all issue tracking - NO markdown TODOs
- Every task, bug, and feature must be filed as a beads issue
- Always include detailed context in issue descriptions

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

### mcp 'nixos' - NixOS Ecosystem
**Use for:** NixOS packages, options, version history, flakes

**Best for:**
- Finding NixOS packages (`nixos_search`)
- Looking up configuration options (`nixos_options_by_prefix`)
- Home Manager settings (`home_manager_info`)
- Package version history (`nixhub_package_versions`)
- Flake searches (`nixos_flakes_search`)

**When to use:**
- ✅ Any NixOS-related work (arda-core is a NixOS orchestration system!)
- ✅ Finding packages to include in NixOS configurations
- ✅ Looking up configuration option details
- ✅ Checking package availability and versions

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
# Research NixOS service configuration for a feature
exa get_code_context_exa --query "nixos service configuration systemd examples" --tokensNum 3000
nixos_search --query "ssh configuration"
exa web_search_exa --query "arda-core nix orchestration patterns" --type deep
```

# 🚨 SESSION CLOSE PROTOCOL 🚨

**CRITICAL**: Before saying "done" or "complete", you MUST run this checklist:

```
[ ] 1. git status              (check what changed)
[ ] 2. git add <files>         (stage code changes)
[ ] 3. bd sync --from-main     (pull beads updates from main)
[ ] 4. git commit -m "..."     (commit code changes)
[ ] 5. git pull --rebase       (pull latest from remote)
[ ] 6. bd sync                 (export issues to JSONL)
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
# Merge to main when ready (local merge, not push)
```

**Creating dependent work:**
```bash
bd create --title="Implement feature X" --type=feature
bd create --title="Write tests for X" --type=task
bd dep add beads-yyy beads-xxx  # Tests depend on Feature (Feature blocks tests)
```
