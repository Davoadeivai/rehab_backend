def safe_print(*args, **kwargs):
    """A safer print function that handles encoding issues with stderr."""
    import sys
    try:
        # Try with the default encoding first
        print(*args, file=sys.stderr, **kwargs)
    except (UnicodeEncodeError, OSError) as e:
        # If that fails, try with a more robust approach
        try:
            import io
            with io.TextIOWrapper(sys.stderr.buffer, errors='replace') as stderr:
                print(*args, file=stderr, **kwargs)
        except Exception:
            # If all else fails, use a very basic write
            try:
                sys.stderr.write(' '.join(str(arg) for arg in args) + '\n')
                sys.stderr.flush()
            except:
                pass  # Give up if we can't even do that
