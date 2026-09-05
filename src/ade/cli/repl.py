"""Interactive REPL for the Ade programming language."""

import sys
from ade import __version__
from ade.diagnostics.reporter import DiagnosticReporter
from ade.lexer.lexer import Lexer
from ade.lexer.errors import LexerError
from ade.parser.parser import Parser
from ade.parser.errors import ParseError
from ade.runtime.environment import Environment
from ade.interpreter.interpreter import Interpreter
from ade.interpreter.errors import AdeRuntimeError


def start_repl() -> None:
    """Start the interactive Ade REPL."""
    print(f"Ade {__version__} Interactive REPL")
    print('Type ".help" for commands, ".exit" to quit.\n')

    environment = Environment()
    reporter = DiagnosticReporter(output_stream=sys.stderr)

    while True:
        try:
            line = input("ade> ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        line = line.strip()
        if not line:
            continue

        if line == ".exit" or line == ".quit":
            print("Goodbye!")
            break

        if line == ".help":
            print("Ade REPL Commands:")
            print("  .help    Show this help message")
            print("  .clear   Clear screen (if terminal supports it)")
            print("  .exit    Exit the REPL")
            print("\nType any valid Ade statement or expression:")
            print("  ade> name = \"Fortune\"")
            print("  ade> say \"Hello \" + name")
            continue

        if line == ".clear":
            print("\033[H\033[J", end="")
            continue

        # Handle multi-line block inputs if braces/parentheses are unbalanced
        source = line
        open_braces = source.count("{") - source.count("}")
        open_parens = source.count("(") - source.count(")")
        open_brackets = source.count("[") - source.count("]")

        while open_braces > 0 or open_parens > 0 or open_brackets > 0:
            try:
                continuation = input(" ... ")
                source += "\n" + continuation
                open_braces = source.count("{") - source.count("}")
                open_parens = source.count("(") - source.count(")")
                open_brackets = source.count("[") - source.count("]")
            except (EOFError, KeyboardInterrupt):
                print("")
                source = ""
                break

        if not source.strip():
            continue

        try:
            lexer = Lexer(source=source, file_path="<repl>")
            tokens = lexer.tokenize()

            parser = Parser(tokens=tokens, source_code=source)
            program = parser.parse()

            interpreter = Interpreter(
                output_stream=sys.stdout,
                source_code=source,
                environment=environment,
            )
            interpreter.interpret(program)

        except LexerError as e:
            reporter.report(e.to_diagnostic())
        except ParseError as e:
            reporter.report(e.to_diagnostic())
        except AdeRuntimeError as e:
            reporter.report(e.to_diagnostic())
        except Exception as e:
            print(f"Internal Error: {e}", file=sys.stderr)
