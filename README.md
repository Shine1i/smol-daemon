# System Maintenance Tools

A collection of Python-based system maintenance tools using the `smolagents` framework to create AI-powered system utilities.

## Features

- **System Cleanup**: Uses BleachBit to clean unnecessary files and free up disk space
- **File Organization**: Automatically organizes folders by file type
- **Smart File Management**: AI-powered decision making for file operations

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd <repository-directory>

# Install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

## Usage

```python
# Run the main agent
python main.py
```

## Requirements

- Python 3.11.0+
- BleachBit (for system cleaning functionality)
- Dependencies listed in requirements.txt

## Project Structure

```
.
├── main.py                 # Main application entry point
├── requirements.txt        # Project dependencies
├── src/
│   └── tools/              # Tool implementations
│       ├── clean_system.py # System cleanup tool
│       └── organize.py     # File organization tool
└── README.md              # This file
```

## License

[MIT](LICENSE)
