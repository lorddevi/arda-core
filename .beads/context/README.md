# Beads Context Files

This directory contains optional rich context files for beads issues.

## Purpose

Context files provide detailed, discoverable documentation for complex issues. They solve the problem of "what was this issue about?" by including:

- User stories and acceptance criteria
- Architecture decisions and constraints
- Implementation notes and logs
- References to code and documentation
- Files changed and impact

## When to Use

**Use context files for:**

- Complex tasks requiring multiple steps
- Architectural changes or decisions
- Bug fixes with non-obvious root causes
- Features requiring design documentation
- Work that future developers will need to understand

**Skip context files for:**

- Simple one-line fixes
- Obvious changes (typos, minor tweaks)
- Quick patches that don't need explanation

## Creating Context Files

1. Create the beads issue first:

   ```bash
   bd create --title="Fix X" --type=task
   ```

2. Copy appropriate template:

   ```bash
   cp .beads/templates/task.md .beads/context/beads-XXX.md
   ```

3. Fill in the template:
   - Replace all `{placeholders}` with actual values
   - Complete all sections relevant to your work
   - Add references to code files

## File Naming

Use the exact beads issue ID:

- `beads-59o.md`
- `beads-xxx.md`

## Updating Context

As work progresses:

- Mark tasks complete: `- [x] Task`
- Add implementation log entries: `**2025-12-01:** Initial implementation`
- Update status field
- Document files changed

## Committing

Always commit context files with related code changes:

```bash
git add .beads/context/beads-XXX.md
git commit -m "feat: implement X (beads-XXX)"
```

## Viewing Context

Anyone can read context files directly:

```bash
cat .beads/context/beads-59o.md
```

## Discovery

Context files improve discoverability by:

- Providing rich, searchable markdown
- Including references to code/docs
- Preserving architectural decisions
- Creating a complete story of the work

This makes it easy for new developers or AI agents to understand:

- Why a change was made
- What problem it solves
- How it was implemented
- What files were affected
