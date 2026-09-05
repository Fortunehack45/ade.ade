# Getting Started with Ade

Welcome to Ade! This guide gets you up and running with writing and executing your first Ade programs.

## Requirements
- Python 3.12+ (for running the reference compiler/interpreter).

## Running Ade

### 1. Running a Script
To execute an Ade script (`.ade`), run:

```bash
python -m ade run path/to/script.ade
```
Or directly with the `ade` command once installed:
```bash
ade run path/to/script.ade
```

### 2. Interactive REPL
To start an interactive Ade shell:

```bash
ade repl
```

Inside the REPL:
```ade
ade> name = "Fortune"
ade> say "Hello, " + name
Hello, Fortune
ade> .exit
```

### 3. Checking Version & Help
```bash
ade --version
ade --help
```
