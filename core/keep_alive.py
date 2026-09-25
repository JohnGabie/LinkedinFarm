import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.orchestrator import BrowserOrchestrator


def main():
    orchestrator = BrowserOrchestrator.instance()
    orchestrator.start()
    print("Browser launched and kept alive. Press Ctrl+C to exit.")

    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("Shutting down...")
        orchestrator.stop()


if __name__ == "__main__":
    main()