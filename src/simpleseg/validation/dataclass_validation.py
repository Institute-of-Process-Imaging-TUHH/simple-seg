from typing import Callable

from loguru import logger
from simpleseg.data.dataclass import AbstractData


def validate_length(dataclass):
    result = len(dataclass) >= 1
    if not result:
        logger.warning(f"It appreas that your dataset is empty: len(dataset) = {len(dataclass)}")
    return result


def validate_name(dataclass):
    result = hasattr(dataclass, "name")
    if not result:
        logger.warning(
            """Your dataclass does not have a name attribute. The name attribute will be shown in the ui to easily
            associate your data. You can add a name attribute by setting dataclass.name = 'custom name'"""
        )
    return result


TESTS: list[Callable] = [validate_length, validate_name]


def validate_data(dataclass: AbstractData):
    counter_success = 0
    for i, t in enumerate(TESTS):
        result = t(dataclass)
        if result:
            counter_success += 1
            logger.debug(f"test {i}/{len(TESTS)} passed successfully")
        else:
            logger.error(f"test {i}/{len(TESTS)} resulted in an error")
    logger.info(f"{counter_success} of {len(TESTS)} tests of dataclass passed successfully")
    if counter_success < len(TESTS):
        raise Exception("Dataclass should pass validate_dataclass() before use")
