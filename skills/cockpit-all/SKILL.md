---
name: cockpit-all
description: "Generate portfolio-level cockpit dashboard across all governed projects"
user_invocable: true
---

# /cockpit-all — Portfolio Cockpit Generator

Generate a portfolio-level HTML dashboard that aggregates status across all governed projects.

## Steps

1. Run the portfolio cockpit generator:
   ```bash
   cd ~/Developer/claude-agent-framework && python -m claude_cli.main cockpit portfolio
   ```
   Or if a specific base directory is requested:
   ```bash
   cd ~/Developer/claude-agent-framework && python -m claude_cli.main cockpit portfolio --base-dir <path>
   ```

2. Report the output path and summary statistics:
   - Number of projects discovered
   - Phase distribution (how many projects in each phase)
   - Total tasks across all projects
   - Any projects with drift or quality gate failures

3. If the user requests a specific project cockpit instead, use `/cockpit` for that project.

## Notes

- Default base directory: `~/Developer`
- Default output: `~/.claude/portfolio_cockpit.html`
- Projects must have `.claude/manifest.yaml` to be discovered
- The generated HTML is self-contained with a dark executive theme
