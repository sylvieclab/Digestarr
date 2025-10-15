# Contributing to Digestarr

First off, thank you for considering contributing to Digestarr! It's people like you that make Digestarr such a great tool for the community.

## Code of Conduct

This project and everyone participating in it is governed by basic principles of respect and professionalism. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

**Bug Report Template:**
- **Description**: Clear description of the bug
- **Steps to Reproduce**: Numbered steps to reproduce the behavior
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened
- **Environment**:
  - OS (Unraid, Ubuntu, etc.)
  - Docker version
  - Digestarr version
  - Plex version
- **Logs**: Relevant logs from `docker logs digestarr`
- **Configuration**: Your `.env` settings (redact sensitive info)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear title** describing the enhancement
- **Detailed description** of the proposed functionality
- **Use case**: Why would this be useful?
- **Possible implementation**: How might this work?
- **Alternatives considered**: What other solutions did you think about?

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following the code style guidelines
3. **Test thoroughly** - ensure your changes work as expected
4. **Update documentation** if you're adding/changing functionality
5. **Write clear commit messages** describing what and why
6. **Submit the pull request** with a clear description

**Pull Request Template:**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How did you test your changes?

## Checklist
- [ ] My code follows the project's style guidelines
- [ ] I have tested my changes
- [ ] I have updated the documentation
- [ ] My changes don't generate new warnings
```

## Development Setup

### Local Development

1. **Clone your fork**:
```bash
git clone https://github.com/YOUR_USERNAME/Digestarr.git
cd Digestarr
```

2. **Create a virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your test configuration
```

5. **Run locally**:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 5667 --reload
```

### Testing Changes

**Manual Testing:**
1. Run Digestarr locally
2. Use Plex webhook test feature
3. Verify Discord messages
4. Check logs for errors

**Docker Testing:**
```bash
docker-compose build
docker-compose up
```

## Code Style Guidelines

### Python Code

- Follow **PEP 8** style guide
- Use **type hints** where appropriate
- Write **docstrings** for functions and classes
- Keep functions **focused and small**
- Use **meaningful variable names**

**Example:**
```python
async def send_digest(self, digest: DigestData) -> bool:
    """
    Send a digest to Discord via webhook.
    
    Args:
        digest: The digest data to send
        
    Returns:
        True if successful, False otherwise
    """
    if not digest or digest.total_items == 0:
        logger.info("No items in digest, skipping send")
        return False
    # ... implementation
```

### File Structure

When adding new features:
- **Models** go in `app/models.py`
- **API routes** go in `app/webhook.py` or create new router
- **Business logic** goes in appropriate module (`aggregator.py`, etc.)
- **Configuration** goes in `app/config.py`

### Commit Messages

Use clear, descriptive commit messages:

**Good:**
```
Add threshold auto-send feature

- Implement DIGEST_THRESHOLD configuration option
- Add unprocessed item counter
- Trigger digest when threshold is met
- Update documentation and configuration examples
```

**Bad:**
```
fixed stuff
```

### Documentation

- Update **README.md** for user-facing changes
- Update **QUICKSTART.md** if setup changes
- Add **inline comments** for complex logic
- Update **configuration examples** in `.env.example`

## Project Structure

```
Digestarr/
├── app/
│   ├── main.py              # FastAPI app, startup/shutdown
│   ├── config.py            # Configuration and settings
│   ├── models.py            # Pydantic models and enums
│   ├── webhook.py           # Webhook endpoints and handling
│   ├── aggregator.py        # Media aggregation and database
│   ├── scheduler.py         # Digest scheduling logic
│   └── discord_sender.py    # Discord webhook integration
├── .github/workflows/       # CI/CD automation
├── data/                    # Database storage (runtime)
├── docker-compose.yml       # Docker deployment
├── Dockerfile              # Container image
├── requirements.txt        # Python dependencies
└── README.md               # Main documentation
```

## Adding New Features

### Example: Adding Email Digest Support

1. **Create email sender module**:
```python
# app/email_sender.py
class EmailSender:
    def __init__(self):
        self.smtp_server = settings.smtp_server
        # ... initialization
    
    async def send_digest(self, digest: DigestData) -> bool:
        # ... implementation
```

2. **Add configuration**:
```python
# app/config.py
class Settings(BaseSettings):
    # ... existing settings
    
    # Email Configuration
    enable_email_digest: bool = False
    smtp_server: Optional[str] = None
    smtp_port: int = 587
    # ... other email settings
```

3. **Integrate into scheduler**:
```python
# app/scheduler.py
from app.email_sender import email_sender

async def send_digest_now():
    # ... existing Discord send code
    
    # Add email sending
    if settings.enable_email_digest:
        await email_sender.send_digest(digest)
```

4. **Update documentation**:
- Add email configuration to README.md
- Add to .env.example
- Update QUICKSTART.md with setup instructions

5. **Test thoroughly** and submit PR

## Questions?

Feel free to open an issue with the `question` label if you have any questions about contributing.

## Recognition

Contributors will be recognized in the README.md and release notes.

Thank you for helping make Digestarr better! 🎉
