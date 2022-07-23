import asyncio
import sys

import qasync
from aiohttp import ClientSession, ClientTimeout
from views import login


async def main():
    """Starts the login window."""
    session = ClientSession(
        loop=asyncio.get_event_loop(),
        timeout=ClientTimeout(total=10),
    )

    login_window = login.Window(session)
    login_window.show()

    await asyncio.Future()


if __name__ == "__main__":
    try:
        qasync.run(main())
    except asyncio.CancelledError:
        sys.exit(0)
