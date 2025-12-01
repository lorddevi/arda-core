# AI Agent Instructions

## Work Tracking
- Use the 'bd' tool for all issue tracking - NO markdown TODOs
- Every task, bug, and feature must be filed as a beads issue
- Always include detailed context in issue descriptions

## MCP Usage
- When working with libraries, check the docs with the mcp 'Ref'
- When you want to reference the master branch for this project 'arda-core' check the repo info using the mcp 'Ref', looking up the resource named 'lorddevi/arda-core'
- When working with NixOS packages, configuration options, home-manager settings, or package version history via nixhub.io, use the mcp 'nixos'
- When working with 'jump' and 'jumpfile' use the mcp 'jump'
- When working with code, use the mcp 'exa' to query the web for examples and to verify understanding of the subject when appropriate
- For any web based queries use the mcp 'exa'
- To research subjects, find relevant information, look up stack over flow questions, or anything like that use the mcp 'exa'

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
