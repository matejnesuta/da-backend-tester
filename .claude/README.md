# Claude Code Configuration

This directory contains custom commands for the DA Backend Tester project.

## Available Commands

### `/create-test` - Create New Test Case
Guides you through creating a new test case:
- Asks about ecosystem (maven, npm, cargo, etc.)
- Understands test type (simple, vulnerabilities, workspace)
- Creates proper directory structure
- Generates manifest files
- Sets up workspace markers if needed

**Example:**
```
/create-test
# Then answer prompts about what you want to create

# Or provide details upfront:
/create-test I want to create an npm test with lodash vulnerability
```

### `/verify-tests` - Validate Test Structure
Scans testfiles/ and verifies all test cases are properly structured:
- Checks for required manifest files
- Validates workspace markers
- Identifies missing lock files
- Reports structural issues

**Example:**
```
/verify-tests
# Scans all test cases

/verify-tests check only npm tests
# Scans specific ecosystem
```

### `/review-snapshots` - Review Snapshot Changes
Helps review snapshot test failures:
- Reads snapshot files from `__snapshots__/`
- Explains what changed
- Identifies patterns across failures
- Recommends accept or investigate
- Shows the right pytest command to update

**Example:**
```
/review-snapshots maven tests are failing
# Reviews maven snapshot differences

/review-snapshots
# Then paste pytest failure output
```

### `/validate-snapshot` - Validate Snapshot Content
Verifies snapshot content matches the manifest file:
- Checks dependencies in snapshot match manifest (production only)
- Verifies dev/build dependencies are NOT in snapshot
- Detects hallucinated packages
- Validates ignore flags are respected
- Checks cross-ecosystem consistency (npm vs pnpm vs yarn, gradle-groovy vs gradle-kotlin)
- Ensures vulnerability counts match across equivalent ecosystems

**Example:**
```
/validate-snapshot testfiles/npm/my_new_test
# Validates the snapshot makes sense for this test

/validate-snapshot
# Prompts for which test to validate

/validate-snapshot check npm vs pnpm consistency
# Compares snapshots across equivalent package managers
```

## How It Works

These commands provide context-specific guidance to Claude Code. When you invoke a command:

1. Claude loads the command's prompt/instructions
2. Claude has access to your repository files via the usual tools (read, write, glob, grep, bash)
3. Claude guides you through the task interactively
4. You can continue the conversation to refine or modify

## Prompt Caching

The commands use Claude's prompt caching automatically:
- Command instructions are cached
- Repository structure is cached after first access
- Repeated invocations are fast and cost-effective

## Tips

**Creating Tests:**
- Use `/create-test` for guided creation
- Answer its questions - it will verify your intent before creating files
- Review generated files before committing

**Verifying Tests:**
- Run `/verify-tests` after creating new tests
- Use it to audit existing test structure
- Helpful before opening PRs

**Reviewing Snapshots:**
- Use `/review-snapshots` after backend updates to compare diffs
- Use `/validate-snapshot` after creating new tests to verify correctness
- Paste pytest failure output for detailed analysis
- Get recommendations on whether to accept changes

## Customization

To modify a command:
1. Edit the `.md` file in `.claude/commands/`
2. Changes take effect immediately (no restart needed)
3. Prompts are version-controlled with your repo

## Adding Your Own Commands

Create a new `.md` file in `.claude/commands/`:

```markdown
# My Custom Command

You are helping with <specific task>.

## Your Role
- What to do
- How to approach it

## Process
1. Step one
2. Step two
```

The filename becomes the command: `my-custom-command.md` → `/my-custom-command`

## Further Reading

- [Claude Code Documentation](https://docs.anthropic.com/claude/docs/claude-code)
- [Custom Commands Guide](https://docs.anthropic.com/claude/docs/custom-commands)
- Main project [README.md](../README.md)
- Workspace testing guide: [testfiles/WORKSPACE_TESTING.md](../testfiles/WORKSPACE_TESTING.md)
