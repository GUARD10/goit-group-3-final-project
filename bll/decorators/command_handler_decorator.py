from functools import wraps
from typing import Callable

from colorama import Fore, Style

from dal.exceptions.exit_bot_error import ExitBotError
from dal.exceptions.invalid_error import InvalidError
from dal.exceptions.not_found_error import NotFoundError
from dal.exceptions.already_exists_error import AlreadyExistsError


def command_handler_decorator(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except ExitBotError:
            raise

        except InvalidError:
            raise

        except NotFoundError:
            raise

        except AlreadyExistsError:
            raise

        except KeyError as ex:
            missing = str(ex).strip("'") if ex.args else "Unknown"
            raise NotFoundError(
                f"{Fore.RED}'{missing}' not found. "
                f"Please check the name and try again.{Style.RESET_ALL}"
            )

        except IndexError:
            raise InvalidError(
                f"{Fore.RED}Invalid command format. "
                f"It looks like you missed one or more arguments."
                f"{Style.RESET_ALL}\n"
                f"Tip: Use '{Fore.CYAN}help{Style.RESET_ALL}' "
                f"to see how to use each command properly."
            )

        except ValueError:
            raise InvalidError(
                f"{Fore.RED}Invalid command format. "
                f"Missing required argument or separator.{Style.RESET_ALL}\n"
                f"Tip: Use '{Fore.CYAN}help{Style.RESET_ALL}' "
                f"to see the correct command format."
            )

        except TypeError:
            raise InvalidError(
                f"{Fore.RED}This command was used incorrectly. "
                f"Some arguments may be missing or extra."
                f"{Style.RESET_ALL}\n"
                f"{Fore.YELLOW} Tip: Use '{Fore.CYAN}help{Style.RESET_ALL}' "
                f"to see how to use each command properly."
            )

        except Exception as ex:
            raise InvalidError(f"Unexpected error: {ex}")

    return wrapper
