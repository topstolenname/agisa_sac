# Python CLI Template

This is a template structure for command-line interface tools.

## Usage

Copy this template to your project directory:

```bash
cp -r assets/templates/python-cli/ /path/to/your/project/
cd /path/to/your/project
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## Structure

```
your-project/
├── src/
│   ├── __init__.py
│   ├── cli.py          # Command-line interface
│   ├── core.py         # Business logic
│   └── utils.py        # Helper functions
├── tests/
│   ├── __init__.py
│   ├── test_cli.py
│   ├── test_core.py
│   └── test_utils.py
├── requirements.txt    # Dependencies
├── setup.py           # Package configuration
├── README.md          # Documentation
└── .gitignore         # Git ignore rules
```

## Customization

1. Rename `src/` to your project name
2. Update `setup.py` with your project details
3. Modify imports in test files
4. Add your specific dependencies to `requirements.txt`

## Testing

```bash
pytest tests/ -v
```

## Building

```bash
pip install -e .  # Editable install for development
# or
python setup.py sdist bdist_wheel  # Build distribution
```
