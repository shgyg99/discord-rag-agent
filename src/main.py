from src.bot.discord_client import run_discord_bot
from src.utils.logger import setup_logger

logger = setup_logger('main')

def main():
    try:
        run_discord_bot()
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
