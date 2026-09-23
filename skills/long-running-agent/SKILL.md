---
name: long-running-agent
description: This skill should be used when developing complex projects that span multiple sessions or context windows. It implements the Long-Running Agent Protocol based on Anthropic's recommended practices for maintaining progress across sessions using SubAgents with isolated context windows, progress tracking files, and incremental feature development.
---

# Long-Running Agent Protocol

This skill provides a systematic approach for developing complex projects across multiple Claude sessions, preventing context loss and maintaining consistent progress.

## When to Use This Skill

- Projects expected to take multiple sessions to complete
- Complex applications with many features (50+ features)
- When delegating tasks to SubAgents for isolated execution
- When previous sessions lost context or progress
- Full-stack applications, CLI tools, or any multi-component project

## Core Concepts

### Master Agent vs SubAgent Architecture

The protocol uses two agent roles:

**Master Agent (You)**: Orchestrates the project, maintains progress files, delegates tasks, and consolidates results.

**SubAgents**: Execute isolated tasks with their own context window, preventing hallucination. Each SubAgent receives a specific task and returns completion status.

### Progress Tracking Files

All progress is tracked in the `.claude/` directory:
```
project/
├── .claude/
│   ├── progress.md          # Session history and status
│   ├── features.xml         # Feature list with status
│   ├── current-task.md      # Task for SubAgent execution
│   └── session-log.md       # Current session activity log
```

## Protocol Workflow

### Phase 1: Session Initialization (Always Execute First)

Before any development work, execute this orientation sequence:

1. **Check for existing progress structure**
```bash
   ls -la .claude/
```

2. **If `.claude/` exists**: Read progress files
   - Read `.claude/progress.md` to understand session history
   - Read `.claude/features.xml` to see pending features
   - Check `git log --oneline -10` for recent commits

3. **If `.claude/` does not exist**: Initialize project
   - Run `scripts/init_project.py` or manually create structure
   - Generate comprehensive feature list (minimum 50 features)
   - Create initial progress.md with session #1

4. **Validate environment**
   - Run development server if applicable
   - Execute basic smoke test
   - If bugs found, fix BEFORE starting new work

5. **Select next task**
   - Choose ONE feature with `status="pending"` from features.xml
   - Prioritize by `priority` attribute (high → medium → low)

### Phase 2: Task Preparation

Before delegating to SubAgent, prepare the task file:

1. Write `.claude/current-task.md` with:
   - Feature ID and description
   - Acceptance criteria (checkboxes)
   - Files to modify
   - Technical context
   - Completion signal phrase

2. Example task file format:
```markdown
   # Current Task

   ## Feature: FEAT-XXX
   **Description**: [Clear description]

   ## Acceptance Criteria
   - [ ] Criterion 1
   - [ ] Criterion 2
   - [ ] Criterion 3

   ## Files to Modify
   - path/to/file1.ts
   - path/to/file2.ts

   ## Technical Context
   [Relevant technical details]

   ## Completion Signal
   When all criteria are met, respond: **TASK_COMPLETE**
   If blocked, respond: **TASK_BLOCKED: [reason]**
```

### Phase 3: SubAgent Execution

Delegate the task to a SubAgent with this prompt pattern:
```
You are a Development SubAgent. Read .claude/current-task.md and execute the described task.

Rules:
- Work incrementally, testing each change
- Do not modify files outside the specified list
- Do not mark criteria complete until verified
- Respond TASK_COMPLETE when all criteria pass
- Respond TASK_BLOCKED: [reason] if you cannot proceed
```

The SubAgent works in isolation with its own context window, preventing hallucination from accumulated context.

### Phase 4: Consolidation (After SubAgent Returns)

When SubAgent responds with completion status:

**If TASK_COMPLETE:**
1. Update `.claude/features.xml` - change status to "complete"
2. Update `.claude/progress.md` - log the completion
3. Commit changes: `git add -A && git commit -m "Feature: FEAT-XXX - [description]"`
4. Update `.claude/session-log.md`
5. Return to Phase 2 for next feature OR end session

**If TASK_BLOCKED:**
1. Log the blocker in `.claude/session-log.md`
2. Decide: break down task further, skip, or request user input
3. Update task and retry OR select different feature

### Phase 5: Session End

Before ending any session:

1. Ensure code compiles and runs
2. Make final git commit if pending changes
3. Update `.claude/progress.md` with session summary
4. Document next steps clearly
5. Leave environment in clean state

## File Formats

### progress.md Format

Reference `references/progress-template.md` for the complete template. Key sections:

- Current session number and date
- Features completed count
- Session history summaries
- Known issues
- Next priorities

### features.xml Format

Reference `references/features-template.xml` for the complete template. Key attributes:

- `id`: Unique feature identifier (FEAT-XXX)
- `status`: pending | in-progress | complete | blocked
- `priority`: high | medium | low
- `session`: Session number when completed

## Critical Rules

### NEVER DO:
- Implement multiple features simultaneously
- Mark features complete without testing
- Skip the orientation phase
- Ignore existing bugs to add new features
- Remove or edit feature descriptions
- End session with broken code

### ALWAYS DO:
- Read progress files before any work
- Work on ONE feature at a time
- Test thoroughly before marking complete
- Commit after each completed feature
- Update progress files after each task
- Leave code in functional state

## Integrating with CLAUDE.md

To make this protocol permanent for a project, append the contents of `assets/claude-md-append.md` to the project's CLAUDE.md file. This ensures the protocol is followed in every session automatically.

## Initialization

For new projects, run the initialization script:
```bash
python scripts/init_project.py --project-name "My Project" --description "Project description"
```

This creates the `.claude/` directory structure and generates an initial feature list based on the project description.