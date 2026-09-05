"""Command-line interface (CLI) for Ade."""

import sys
import os
from ade import __version__
from ade.diagnostics.reporter import DiagnosticReporter
from ade.lexer.lexer import Lexer
from ade.lexer.errors import LexerError
from ade.parser.parser import Parser
from ade.parser.errors import ParseError
from ade.interpreter.interpreter import Interpreter
from ade.interpreter.errors import AdeRuntimeError
from ade.cli.repl import start_repl


HELP_TEXT = f"""Ade Programming Language — CLI (v{__version__})

Usage:
  ade run <file.ade>    Execute an Ade source file
  ade repl              Launch the interactive REPL
  ade --version, -v     Show current Ade version
  ade --help, -h        Show this help message

Future Language-Development Commands:
  ade build <file.ade>  (Scheduled for Phase 11)
  ade test              (Scheduled for Phase 8)
  ade fmt               (Scheduled for Phase 14)
  ade check             (Scheduled for Phase 7)
  ade package           (Scheduled for Phase 6)
  ade lang new <name>   (Scheduled for Phase 13)
"""


def run_file(file_path: str) -> int:
    """Execute an Ade source file. Returns process exit code (0 = success, 1 = failure)."""
    if not os.path.exists(file_path):
        print(f"Error: file '{file_path}' does not exist.", file=sys.stderr)
        return 1

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}", file=sys.stderr)
        return 1

    reporter = DiagnosticReporter(output_stream=sys.stderr)

    try:
        lexer = Lexer(source=source, file_path=file_path)
        tokens = lexer.tokenize()

        parser = Parser(tokens=tokens, source_code=source)
        program = parser.parse()

        interpreter = Interpreter(source_code=source, current_file_path=file_path)
        interpreter.interpret(program)
        return 0

    except LexerError as e:
        reporter.report(e.to_diagnostic())
        return 1
    except ParseError as e:
        reporter.report(e.to_diagnostic())
        return 1
    except AdeRuntimeError as e:
        reporter.report(e.to_diagnostic())
        return 1
    except Exception as e:
        print(f"Internal Error: {e}", file=sys.stderr)
        return 1


def main(argv: list[str] | None = None) -> int:
    """Entry point for the 'ade' executable and 'python -m ade'."""
    args = list(sys.argv[1:] if argv is None else argv)

    if not args:
        print(HELP_TEXT)
        return 0

    command = args[0]

    if command in ("--version", "-v"):
        print(f"Ade {__version__}")
        return 0

    if command in ("--help", "-h"):
        print(HELP_TEXT)
        return 0

    if command == "repl":
        start_repl()
        return 0

    if command == "run":
        if len(args) < 2:
            print("Error: Missing file path.\nUsage: ade run <file.ade>", file=sys.stderr)
            return 1
        return run_file(args[1])

    # Unimplemented future commands
    future_commands = {
        "build": "Phase 11 (Bytecode/Native compilation)",
        "test": "Phase 8 (Standard testing framework)",
        "fmt": "Phase 14 (Code formatter)",
        "check": "Phase 7 (Static type checker)",
        "package": "Phase 6 (Package management)",
        "lang": "Phase 13 (Language-building platform commands)",
    }

    if command in future_commands:
        target_phase = future_commands[command]
        print(
            f"Note: Command 'ade {command}' is scheduled for {target_phase} and is not yet implemented.\n"
            f"Run 'ade --help' to see currently supported commands.",
            file=sys.stderr,
        )
        return 1

    # Check if a .ade file was passed directly without "run"
    if command.endswith(".ade"):
        return run_file(command)

    print(f"Unknown command: '{command}'. Run 'ade --help' for usage.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
