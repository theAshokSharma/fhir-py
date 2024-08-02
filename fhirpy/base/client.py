from abc import ABC, abstractmethod
from typing import Any, TypeVar, Union

from yarl import URL

from fhirpy.base.utils import (
    encode_params,
    remove_prefix,
)


class AbstractClient(ABC):
    url: str
    authorization: Union[str, None]
    extra_headers: Union[dict, None]

    def __init__(
        self,
        url: str,
        authorization: Union[str, None] = None,
        extra_headers: Union[dict, None] = None,
    ):
        self.url = url
        self.authorization = authorization
        self.extra_headers = extra_headers

    def __str__(self):
        return f"<{self.__class__.__name__} {self.url}>"

    def __repr__(self):
        return self.__str__()

    @abstractmethod
    def reference(self, resource_type=None, id=None, reference=None, **kwargs):  # noqa: A002
        pass

    @abstractmethod
    def resource(self, resource_type, **kwargs):
        pass

    @abstractmethod
    def resources(self, resource_type):
        pass

    @abstractmethod
    def execute(
        self,
        path: str,
        method: str = "post",
        data: Union[dict, None] = None,
        params: Union[dict, None] = None,
    ):
        pass

    @abstractmethod
    def save(self, resource, fields):
        pass

    @abstractmethod
    def create(self, resource):
        pass

    @abstractmethod
    def update(self, resource):
        pass

    @abstractmethod
    def patch(self, resource_type, id, **kwargs):  # noqa: A002
        pass

    @abstractmethod
    def delete(self, resource_type, id):  # noqa: A002
        pass

    @abstractmethod
    def _do_request(
        self,
        method: str,
        path: str,
        data: Union[dict, None] = None,
        params: Union[dict, None] = None,
        returning_status=False,
    ) -> Union[Any, tuple[Any, int]]:
        pass

    @abstractmethod
    def _fetch_resource(self, path, params=None):
        pass

    def _build_request_headers(self) -> dict:
        headers = {"Accept": "application/fhir+json"}

        if self.authorization:
            headers["Authorization"] = self.authorization

        if self.extra_headers is not None:
            headers = {**headers, **self.extra_headers}

        return headers

    def _build_request_url(self, path, params) -> str:
        if URL(path).is_absolute():
            if self.url in path:
                return path
            raise ValueError(
                f'Request url "{path}" does not contain base url "{self.url}"'
                " (possible security issue)"
            )
        path = path.lstrip("/")
        base_url_path = URL(self.url).path.lstrip("/") + "/"
        path = remove_prefix(path, base_url_path)
        params = params or {}

        return f'{self.url.rstrip("/")}/{path.lstrip("/")}?{encode_params(params)}'


TClient = TypeVar("TClient", bound=AbstractClient)
