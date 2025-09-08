import sys
import io
from django.core.mail.backends.console import EmailBackend as ConsoleEmailBackend

class UnicodeConsoleEmailBackend(ConsoleEmailBackend):
    def write_message(self, message):
        # Force UTF-8 encoding for the console output
        if hasattr(sys.stdout, 'encoding') and sys.stdout.encoding != 'utf-8':
            try:
                sys.stdout = io.TextIOWrapper(
                    sys.stdout.buffer,
                    encoding='utf-8',
                    errors='replace',
                    newline='\n',
                    line_buffering=True
                )
            except (AttributeError, io.UnsupportedOperation):
                # If we can't modify stdout, just continue with the default
                pass
        super().write_message(message)
