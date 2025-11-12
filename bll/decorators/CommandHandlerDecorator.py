from functools import wraps
from typing import Callable

from dal.Exceptions.ExitBotException import ExitBotException
from dal.Exceptions.InvalidException import InvalidException
from dal.Exceptions.NotFoundException import NotFoundException


def command_handler_decorator(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except ExitBotException:
            raise

        except KeyError as ex:
            missing = str(ex).strip("'") if ex.args else "Unknown"
            raise NotFoundException(f"'{missing}' not found. Please check the name and try again.")

        except IndexError:
            raise InvalidException(
                "Invalid command format. It looks like you missed one or more arguments.\n"
                "Tip: Use 'help' to see how to use each command properly."
            )

        except ValueError:
            raise InvalidException(
                "Invalid data format. Please make sure you entered the correct number of arguments "
                "and separated them with spaces.\n"
                "Tip: Use 'help' to see how to use each command properly."
            )

        except TypeError:
            raise InvalidException(
                "This command was used incorrectly. Some arguments may be missing or extra.\n"
                "Tip: Use 'help' to see how to use each command properly."
            )

        except Exception as ex:
            raise InvalidException(f"Unexpected error: {ex}")

    return wrapper
