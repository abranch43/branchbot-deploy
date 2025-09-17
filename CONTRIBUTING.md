# Contributing to branchbot-deploy

Thank you for your interest in contributing to branchbot-deploy! This document provides guidelines for contributing to this project.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- pip package manager
- Git

### Development Setup

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/your-username/branchbot-deploy.git
   cd branchbot-deploy
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run tests to verify setup:**
   ```bash
   python -m unittest branchbot/test_minimal.py
   ```

## Development Workflow

### Making Changes

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes following our coding standards:**
   - Follow PEP 8 for Python code style
   - Use 4 spaces for indentation
   - Add docstrings for new functions and classes
   - Keep line length under 88 characters

3. **Test your changes:**
   ```bash
   python -m unittest branchbot/test_minimal.py
   ```

4. **Commit with descriptive messages:**
   ```bash
   git commit -m "feat: add new webhook validation feature"
   ```

### Pull Request Process

1. **Ensure your PR includes:**
   - [ ] Clear description of changes
   - [ ] Tests for new functionality
   - [ ] Updated documentation if needed
   - [ ] No secrets or sensitive data committed

2. **PR Checklist:**
   - [ ] Tests pass locally
   - [ ] Code follows style guidelines
   - [ ] No merge conflicts with main branch
   - [ ] Descriptive commit messages
   - [ ] Request review from @abranch43 or @Copilot

3. **Wait for code review and address feedback**

## Code Style Guidelines

### Python Code
- Follow PEP 8 style guide
- Use type hints where appropriate
- Add docstrings for public functions
- Keep functions focused and small
- Use meaningful variable names

### Security Guidelines

- **Never commit secrets:** Use environment variables for API keys, tokens, and passwords
- **Validate input:** Always validate and sanitize user input
- **Use HTTPS:** Ensure all external communications use HTTPS
- **Keep dependencies updated:** Regularly update requirements.txt

### Testing Guidelines

- Write tests for new functionality
- Ensure existing tests continue to pass
- Use descriptive test names
- Test both success and failure cases

## Reporting Issues

### Bug Reports

Use the [issue template](.github/ISSUE_TEMPLATE.md) and include:
- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Environment details (Python version, OS, etc.)
- Relevant logs or error messages

### Feature Requests

- Describe the feature and its use case
- Explain why it would be valuable
- Consider implementation approaches
- Check if similar features already exist

## Security

### Reporting Security Vulnerabilities

Please see our [Security Policy](SECURITY.md) for reporting security issues.

### Security Best Practices

- Enable 2FA on your GitHub account
- Use secure coding practices
- Keep dependencies up to date
- Never include secrets in commits

## Community and Support

- **Discussions:** Use GitHub Discussions for questions and ideas
- **Issues:** Use GitHub Issues for bugs and feature requests
- **Reviews:** All code changes require review before merging

## Recognition

Contributors will be recognized in our README.md and release notes. Thank you for helping make branchbot-deploy better!

## License

By contributing to branchbot-deploy, you agree that your contributions will be licensed under the MIT License.