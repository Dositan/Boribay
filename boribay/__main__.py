import asyncio
import logging
import sys

from boribay.core.bot import Boribay

from .cli import parse_flags, parse_single_flags
from .log import init_logging

log = logging.getLogger('bot.main')


def main() -> None:
    """The main function of the bot that exactly manages the Boribay app."""
    init_logging(level=logging.INFO)

    args = parse_flags(sys.argv[1:])
    bot = Boribay(cli_flags=args)
    parse_single_flags(args)

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.create_task(bot.start())
        loop.run_forever()
    except Exception as exc:  # Unhandled exception.
        log.exception(f'Unhandled exception ({type(exc)}): ', exc_info=exc)
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        log.info('Cleaning up...')
        loop.run_until_complete(asyncio.sleep(2))
        asyncio.set_event_loop(None)
        loop.stop()
        loop.close()
        sys.exit(0)


if __name__ == '__main__':
    main()
