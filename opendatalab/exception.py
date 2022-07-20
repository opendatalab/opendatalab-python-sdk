#!/usr/bin/env python3
#
# Copyright 2022 Shanghai AI Lab. Licensed under MIT License.
#
from typing import Optional, TYPE_CHECKING, Union

class OpenDataLabError(Exception):
    """
    This is the base class for OpenDataLab custom exceptions.

    Args:
        Exception (str): the error message
    """
    def __init__(
        self,
        response_code: Optional[int] = None,
        error_message: str = "",
    ) -> None:

        super().__init__(self, error_message)
        self.response_code = response_code
        self.error_message = error_message


    def __str__(self) -> str:
        if self.response_code is not None:
            return f"{self.response_code}: {self.error_message}"
        else:
            return f"{self.error_message}"


class OpenDataLabAuthError(OpenDataLabError):
    def __init__(self, response_code: Optional[int] = None, error_message: str = "") -> None:
        super().__init__(response_code, error_message)




class OdlDatasetAccessDeniedError(OpenDataLabError):
    def __init__(self, response_code: Optional[int] = None, error_message: str = "") -> None:
        super().__init__(response_code, error_message)

    pass

class OdlDatasetNotExistsError(OpenDataLabError):
    def __init__(self, response_code: Optional[int] = None, error_message: str = "") -> None:
        super().__init__(response_code, error_message)
        
    pass

class OdlRequestNeedToken(OpenDataLabError):
    def __init__(self, response_code: Optional[int] = None, error_message: str = "") -> None:
        super().__init__(response_code, error_message)
        
    pass