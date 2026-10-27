# Commit Message Convention

This project follows **Conventional Commits** (https://www.conventionalcommits.org).
All commits generated or suggested by Claude must conform to this spec.

## Format
<type>[optional scope]: <description>
[optional body]
[optional footer(s)]

## Allowed types

- feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert

## Scopes for this project (pick the closest match)

- python, research

## Rules

1. Subject line ≤ 72 characters, lowercase, no trailing period.
2. Use imperative mood: "add feature" not "added feature".
3. Breaking changes: append `!` to the type OR add a `BREAKING CHANGE:` footer.
4. Never squash unrelated changes into one commit — split them.
