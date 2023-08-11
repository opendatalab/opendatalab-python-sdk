#!/usr/bin/env python3
#
# Copyright 2022 Shanghai AI Lab. Licensed under MIT License.
#
from typing import Optional


class OpenDataLabError(Exception):
    """
    Base class for OpenDataLab custom exceptions.
    """

    def __init__(self, resp_code: Optional[int] = None, error_msg: str = ""):
        super().__init__(self, error_msg)
        self.resp_code = resp_code
        self.error_msg = error_msg

    def __str__(self) -> str:
        if self.resp_code:
            return f"{self.resp_code}: {self.error_msg}"
        else:
            return f"{self.error_msg}"


class RespError(OpenDataLabError):
    """

    """
    STATUS_CODE: int
    _INDENT = " " * len(__qualname__)  # type: ignore

    def __init__(self, resp_code: Optional[int] = None, error_msg: str = ""):
        super().__init__(resp_code, error_msg)

    def __init_subclass__(cls, **kwargs) -> None:
        cls._INDENT = " " * len(cls.__name__)

    def __str__(self) -> str:
        if hasattr(self, "resp_code"):
            return f"Error: {self.STATUS_CODE}, error_msg: {self.error_msg}"

        return super().__str__()


class OdlAuthError(RespError):
    STATUS_CODE = 401


class OdlAccessDeniedError(RespError):
    STATUS_CODE = 403


class OdlDataNotExistsError(RespError):
    STATUS_CODE = 404


class OdlAccessCdnError(RespError):
    STATUS_CODE = 412


class InternalServerError(RespError):
    STATUS_CODE = 500
