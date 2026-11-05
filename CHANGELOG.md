# Changelog

## 2026-11-05

### Fixed
- `wake-streamlit` job failed after the `ubuntu-latest` label moved to Ubuntu 26.04
  (`apt-key` was removed from the image). Replaced the manual Chrome install
  with `browser-actions/setup-chrome`.

### Improved
- `wake_app.py`: retries up to 2 times per app, keeps going when one app fails,
  exits non-zero if any app fails, and verifies that the app actually woke up.
- Workflow: least-privilege `permissions`, `timeout-minutes`, `concurrency`,
  pip caching, and a safer commit/push step (`git pull --rebase`).
- Upgraded GitHub Actions to Node 24 versions (checkout, setup-python, setup-chrome).
