#!/bin/bash
# Helper script to create beads context files
# Usage: ./create-context.sh <issue-id> <type>
# Example: ./create-context.sh beads-59o task

set -e

if [ $# -ne 2 ]; then
    echo "Usage: $0 <issue-id> <type>"
    echo "Types: task, bug, feature"
    exit 1
fi

ISSUE_ID="$1"
TYPE="$2"
TEMPLATE_DIR=".beads/templates"
CONTEXT_DIR=".beads/context"

# Validate type
if [ "$TYPE" != "task" ] && [ "$TYPE" != "bug" ] && [ "$TYPE" != "feature" ]; then
    echo "Error: Type must be 'task', 'bug', or 'feature'"
    exit 1
fi

# Check if template exists
TEMPLATE_FILE="$TEMPLATE_DIR/$TYPE.md"
if [ ! -f "$TEMPLATE_FILE" ]; then
    echo "Error: Template not found: $TEMPLATE_FILE"
    exit 1
fi

# Create context file
CONTEXT_FILE="$CONTEXT_DIR/$ISSUE_ID.md"
if [ -f "$CONTEXT_FILE" ]; then
    echo "Error: Context file already exists: $CONTEXT_FILE"
    exit 1
fi

# Copy template
cp "$TEMPLATE_FILE" "$CONTEXT_FILE"

# Replace placeholders with issue ID (status defaults to "open")
sed -i "s/{id}/$ISSUE_ID/g" "$CONTEXT_FILE"
sed -i "s/{status}/open/g" "$CONTEXT_FILE"

echo "✅ Created context file: $CONTEXT_FILE"
echo ""
echo "Next steps:"
echo "1. Edit the file and fill in all {placeholders}"
echo "2. Add your user story and acceptance criteria"
echo "3. Commit: git add .beads/context/$ISSUE_ID.md"
