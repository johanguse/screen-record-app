import time

def retry_operation(operation, max_attempts=3, delay=1):
    for attempt in range(max_attempts):
        try:
            return operation()
        except PermissionError as e:
            if attempt == max_attempts - 1:
                raise
            print(f"Permission error, retrying in {delay} seconds...")
            time.sleep(delay)