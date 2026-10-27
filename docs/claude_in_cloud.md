# Developing seenery in Claude cloud (and managing it from a phone)

Claude Code on the web runs sessions in an isolated cloud VM that clones the
repo from GitHub. Menu names may differ slightly in the current UI.

## 1. Push your local state first

The cloud session clones from GitHub, so anything not pushed is invisible to it.

1. Commit in logical chunks, following the Conventional Commits rules in
   `CLAUDE.md`.
2. `git push origin main`

## 2. Connect GitHub to Claude

1. Open <https://claude.ai/code> (requires a Pro or Max plan).
2. Click **Connect GitHub** and install the **Claude GitHub app**.
3. Grant it access to `lacuna-core/seenery`. You may need an org owner to
   approve the install.

## 3. Create a cloud environment

1. In claude.ai/code, open the environment selector and choose
   **Add/Edit environment**.
2. Set the setup script to:
   ```bash
   bash sh/init_vm.sh
   ```
3. Set network access. Installing from PyPI needs at least the default
   "trusted" level.
4. Add environment variables, e.g. any `LACUNA_*` settings. `.env` is not in
   git. Environment variables are visible to anyone who can edit the
   environment, so do not put real secrets there.

## 4. Start a session

1. Pick the repo `lacuna-core/seenery` and a branch.
2. Describe the task, e.g. "add a `version` subcommand with tests".
3. Claude reads `CLAUDE.md`, so it follows the uv, ruff, mypy and commit
   conventions.
4. When done, Claude pushes to a new branch and can open a PR. Review the diff
   in the web UI.


### Which branch to select

The selected branch is the **base**, not the push target. The session clones it
and works on a new `claude/...` branch; it does not push to `main` by default.
Open a PR from that branch into the base, and merge it yourself.

## 5. Manage it from your phone

1. Install the **Claude iOS or Android app** and sign in with the same account.
2. Open the **Code** tab, where your cloud sessions appear.
3. Start tasks, watch progress, answer questions, steer a running session and
   review diffs.
4. Merge via the GitHub mobile app, or ask Claude to open/update the PR.
5. Enable push notifications to be alerted when a session finishes or needs
   input.

## 6. Optional: continue locally

- `claude --teleport` pulls a cloud session into your terminal.
- `claude --remote "task"` starts a cloud session from the CLI, which you can
  then follow from your phone.

## Practical advice

- Keep tasks small and well scoped: one PR per task.
- Put new conventions in `CLAUDE.md` so every session picks them up.
- Do not store real secrets in the environment.
