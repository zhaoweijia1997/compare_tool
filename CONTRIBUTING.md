# Contributing to PyCompare

Thank you for your interest in contributing to PyCompare! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with the following information:

- A clear and descriptive title
- Steps to reproduce the bug
- Expected behavior
- Actual behavior
- Screenshots (if applicable)
- Your environment (OS, Python version, etc.)

### Suggesting Enhancements

We welcome suggestions for new features or improvements! Please create an issue with:

- A clear and descriptive title
- Detailed description of the proposed feature
- Explanation of why this feature would be useful
- Examples of how it would work (if applicable)

### Pull Requests

1. **Fork the repository** and create your branch from `main`
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make your changes**
   - Write clear, readable code
   - Follow the existing code style
   - Add comments where necessary
   - Update documentation if needed

3. **Test your changes**
   - Ensure the application runs without errors
   - Test both file and folder comparison features
   - Test on different file types and encodings if applicable

4. **Commit your changes**
   ```bash
   git commit -m "Add some feature"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/my-new-feature
   ```

6. **Create a Pull Request**
   - Provide a clear description of the changes
   - Reference any related issues
   - Wait for review and address any feedback

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git

### Setup Steps

1. Clone your fork
   ```bash
   git clone https://github.com/your-username/pycompare.git
   cd pycompare
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application
   ```bash
   python main.py
   ```

## Code Style Guidelines

### Python Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use meaningful variable and function names
- Maximum line length: 100 characters (flexible)
- Use type hints where appropriate

### Docstrings

Use Google-style docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """Brief description of function.

    Longer description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value
    """
    pass
```

### Imports

Group imports in the following order:
1. Standard library imports
2. Third-party imports
3. Local application imports

```python
import os
import sys

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt

from src.core.diff_engine import DiffEngine
```

## Project Structure

```
compare_tool/
├── main.py                 # Application entry point
├── src/
│   ├── core/              # Core logic (diff algorithm, etc.)
│   ├── ui/                # UI components
│   └── utils/             # Utility functions
├── resources/             # Static resources
└── tests/                 # Unit tests (to be added)
```

### Where to Add Your Code

- **Core functionality**: Add to `src/core/`
- **UI components**: Add to `src/ui/`
- **Utility functions**: Add to `src/utils/`
- **Resources**: Add to `resources/`

## Testing

While we don't have a formal test suite yet, please manually test:

- File comparison with various file types
- Folder comparison with different structures
- Edge cases (empty files, binary files, large files)
- UI responsiveness

## Documentation

When adding new features:

- Update relevant docstrings
- Add comments for complex logic
- Update README.md if it affects user-facing features
- Update CHANGELOG.md

## Questions?

If you have questions about contributing, feel free to:

- Open an issue with the "question" label
- Contact the maintainers

## Code of Conduct

Be respectful and constructive in all interactions. We aim to foster an inclusive and welcoming community.

## License

By contributing to PyCompare, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to PyCompare!
