# Contributing to HydroGenerate

Thank you for your interest in contributing to HydroGenerate! We welcome contributions of all kinds—bug reports, feature requests, documentation improvements, and code enhancements.

This guide will help you get started.

---
## How to Contribute

1. **Fork the repository** and clone it locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/HydroGenerate.git
   cd HydroGenerate
   ```

2. **Create a new branch** for your feature or fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**, commit, and push:
   ```bash
   git add .
   git commit -m "ENH: Add new feature description"
   git push origin feature/your-feature-name
   ```

4. **Open a Pull Request** on GitHub and describe your changes clearly.

---

## Development Setup

We recommend using `conda` for environment management:

```bash
conda create --name hg-env python=3.10
conda activate hg-env
pip install -e HydroGenerate
```

---

## Submitting a Pull Request

- Use clear and descriptive commit messages.
- Prefix PR titles with:
  - `ENH:` for enhancements
  - `BUG:` for bug fixes
  - `DOC:` for documentation
  - `TST:` for tests
  - `CLN:` for cleanup

- Link to any related issues using `Closes #issue_number`.
- Ensure your branch is up to date with `main` before submitting.

---
## Feature Requests

We welcome ideas to improve HydroGenerate! If you have a feature in mind:

1. **Search existing issues** to see if it's already been proposed.
2. If not, **open a new issue**.
3. Clearly describe:
   - The problem you're trying to solve
   - Why it's important
   - A possible solution or implementation idea (if you have one)

We encourage discussion and feedback from the community before implementation.

---

## Documentation Improvements

Improving documentation is a great way to contribute!

You can help by:
- Fixing typos or grammar
- Clarifying examples or explanations
- Adding new usage examples or tutorials
- Improving docstrings in the code

To contribute:
1. Make your edits in the appropriate `.md` or `.py` files.
2. Follow the same process as for code contributions (fork, branch, PR).
3. Preview your changes locally if possible.

---

## Style Guide

- Follow PEP8 for Python code.
- Use [Google-style docstrings](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html).
- Format code with [`black`](https://black.readthedocs.io/en/stable/) and check with [`flake8`](https://flake8.pycqa.org/en/latest/).

---

## Community

We encourage open discussion and collaboration. If you have questions or ideas:
- Open an issue
- Join our discussions (if applicable)
- Reach out via GitHub

---

## References

- [GitHub Docs: Setting Guidelines](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/setting-guidelines-for-repository-contributors)
- [GitHub Docs: Contributing to Open Source](https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-open-source)
- [pandas Contributing Guide](https://pandas.pydata.org/docs/development/contributing.html)
```
