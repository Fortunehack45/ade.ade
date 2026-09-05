"""Command-line interface (CLI) for Ade."""

import sys
import os
from ade import __version__
from ade.diagnostics.reporter import DiagnosticReporter
from ade.diagnostics.diagnostic import DiagnosticSeverity
from ade.lexer.lexer import Lexer
from ade.lexer.errors import LexerError
from ade.parser.parser import Parser
from ade.parser.errors import ParseError
from ade.interpreter.interpreter import Interpreter
from ade.interpreter.errors import AdeRuntimeError
from ade.semantic.checker import TypeChecker
from ade.cli.repl import start_repl


HELP_TEXT = f"""Ade Programming Language — CLI (v{__version__})

Usage:
  ade run <file.ade>            Execute an Ade source file
  ade check <file.ade>          Perform static type checking
  ade dsl <spec.ade> <file.dsl> Execute a custom DSL script using an Ade specification
  ade repl                      Launch the interactive REPL
  ade --version, -v             Show current Ade version
  ade --help, -h                Show this help message

Future Language-Development Commands:
  ade build <file.ade>  (Scheduled for Phase 11)
  ade test              (Scheduled for Phase 8)
  ade fmt               (Scheduled for Phase 14)
  ade package           (Scheduled for Phase 6)
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


def check_file(file_path: str) -> int:
    """Run static type checking and semantic analysis on an Ade source file. Returns 0 if clean, 1 if errors."""
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

        checker = TypeChecker(source_code=source)
        diagnostics = checker.check(program)

        if diagnostics:
            for diag in diagnostics:
                reporter.report(diag)
            error_count = sum(1 for d in diagnostics if d.severity == DiagnosticSeverity.ERROR)
            warn_count = sum(1 for d in diagnostics if d.severity == DiagnosticSeverity.WARNING)
            if error_count > 0:
                print(f"\nType check failed with {error_count} error(s) and {warn_count} warning(s).", file=sys.stderr)
                return 1
            else:
                print(f"Type check completed with {warn_count} warning(s).")
                return 0

        print(f"Success: All type checks passed for '{file_path}'.")
        return 0

    except LexerError as e:
        reporter.report(e.to_diagnostic())
        return 1
    except ParseError as e:
        reporter.report(e.to_diagnostic())
        return 1
    except Exception as e:
        print(f"Internal Error: {e}", file=sys.stderr)
        return 1


def run_dsl(spec_path: str, dsl_path: str) -> int:
    """Execute an Ade specification file to configure a DSL, then parse & run the DSL file."""
    if not os.path.exists(spec_path):
        print(f"Error: spec file '{spec_path}' does not exist.", file=sys.stderr)
        return 1
    if not os.path.exists(dsl_path):
        print(f"Error: DSL file '{dsl_path}' does not exist.", file=sys.stderr)
        return 1

    try:
        with open(spec_path, "r", encoding="utf-8") as f:
            spec_source = f.read()
        with open(dsl_path, "r", encoding="utf-8") as f:
            dsl_source = f.read()
    except Exception as e:
        print(f"Error reading files: {e}", file=sys.stderr)
        return 1

    reporter = DiagnosticReporter(output_stream=sys.stderr)

    try:
        # 1. Execute spec file
        lexer = Lexer(source=spec_source, file_path=spec_path)
        tokens = lexer.tokenize()
        parser = Parser(tokens=tokens, source_code=spec_source)
        program = parser.parse()

        interpreter = Interpreter(source_code=spec_source, current_file_path=spec_path)
        interpreter.interpret(program)

        # 2. Look for the engine instance in the environment
        engine_val = None
        for name in ("engine", "dsl", "calc", "query", "lang", "app"):
            candidate = interpreter.environment.values.get(name)
            if candidate is not None and hasattr(candidate, "fields") and "execute" in candidate.fields:
                engine_val = candidate
                break

        if engine_val is None:
            # Look for any AdeInstance with an execute field
            for name, val in interpreter.environment.values.items():
                if hasattr(val, "fields") and "execute" in val.fields:
                    engine_val = val
                    break

        if engine_val is None:
            print(f"Error: Spec file '{spec_path}' did not define a DSL engine (e.g. 'engine = language.create(...)').", file=sys.stderr)
            return 1

        exec_fn = engine_val.fields["execute"]
        from ade.runtime.value import AdeString
        from ade.diagnostics.span import SourceLocation, SourceSpan
        span = tokens[-1].span if tokens else SourceSpan.from_single(SourceLocation(spec_path, 1, 1, 0))
        res = exec_fn.call(interpreter, [AdeString(dsl_source)], span)
        if not (hasattr(res, "value") and res.value is None):
            print(res.to_string())
        return 0

    except (LexerError, ParseError, AdeRuntimeError) as e:
        reporter.report(e.to_diagnostic())
        return 1
    except Exception as e:
        print(f"DSL Execution Error: {e}", file=sys.stderr)
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

    if command == "check":
        if len(args) < 2:
            print("Error: Missing file path.\nUsage: ade check <file.ade>", file=sys.stderr)
            return 1
        return check_file(args[1])

    if command == "dsl":
        if len(args) < 3:
            print("Error: Missing arguments.\nUsage: ade dsl <spec.ade> <file.dsl>", file=sys.stderr)
            return 1
        return run_dsl(args[1], args[2])

    # Unimplemented future commands
    future_commands = {
        "build": "Phase 11 (Bytecode/Native compilation)",
        "test": "Phase 8 (Standard testing framework)",
        "fmt": "Phase 14 (Code formatter)",
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
