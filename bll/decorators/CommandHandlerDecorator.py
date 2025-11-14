from functools import wraps
from typing import Callable

from dal.exceptions.ExitBotException import ExitBotException
from dal.exceptions.InvalidException import InvalidException
from dal.exceptions.NotFoundException import NotFoundException

from colorama import Fore as cf
from colorama import Style as cs


def command_handler_decorator(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except ExitBotException:
            raise

        except KeyError as ex:
            missing = str(ex).strip("'") if ex.args else "Unknown"
            raise NotFoundException(
                f"{cf.RED}'{missing}' not found. Please check the name and try again.{cs.RESET_ALL}"
            )

        except IndexError:
            raise InvalidException(
                f"{cf.RED}Invalid command format. It looks like you missed one or more arguments.{cs.RESET_ALL}\n"
                f"Tip: Use '{cf.CYAN}help{cs.RESET_ALL}' to see how to use each command properly."
            )

        except ValueError as e:
            msg = str(e).strip()
            raise InvalidException(msg)

        except TypeError:
            raise InvalidException(
                f"{cf.RED}This command was used incorrectly. Some arguments may be missing or extra.{cs.RESET_ALL}\n"
                f"Tip: Use '{cf.CYAN}help{cs.RESET_ALL}' to see how to use each command properly."
            )

        except Exception as ex:
            raise InvalidException(f"Unexpected error: {ex}")

    return wrapper
