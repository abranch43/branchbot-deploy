import os
import sys

# Add the contracts bot package root so `import contracts_bot` works in tests
BOT_PKG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "bots", "contracts-bot")
)
if BOT_PKG_PATH not in sys.path:
    sys.path.insert(0, BOT_PKG_PATH)
