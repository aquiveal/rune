from typing import Literal

from pydantic import BaseModel, Field, model_validator

__all__ = [
    "McpBase",
    "McpRegistryEntry",
    "McpServerUnion",
    "McpSettings",
    "McpSseServer",
    "McpStdioServer",
    "McpStreamableHttpServer",
]


class McpBase(BaseModel):
    disabled: bool = False
    timeout: int = Field(60, ge=1, le=3600)
    alwaysAllow: list[str] | None = None
    disabledTools: list[str] | None = None
    watchPaths: list[str] | None = None


class McpStdioServer(McpBase):
    type: Literal["stdio"] = "stdio"
    command: str = Field(..., min_length=1)
    args: list[str] | None = None
    env: dict[str, str] | None = None
    cwd: str | None = None

    @model_validator(mode="before")
    @classmethod
    def validate_no_http_fields(cls, data: object) -> object:
        if isinstance(data, dict) and ("url" in data or "headers" in data):
            raise ValueError(
                "stdio transport must not contain 'url' or 'headers' fields."
            )
        return data


class McpSseServer(McpBase):
    type: Literal["sse"] = "sse"
    url: str = Field(..., min_length=1)
    headers: dict[str, str] | None = None

    @model_validator(mode="before")
    @classmethod
    def validate_no_stdio_fields(cls, data: object) -> object:
        if isinstance(data, dict):
            forbidden = {"command", "args", "env", "cwd"}
            found = forbidden.intersection(data.keys())
            if found:
                raise ValueError(
                    f"sse transport must not contain stdio fields: {', '.join(sorted(found))}"
                )
        return data


class McpStreamableHttpServer(McpBase):
    type: Literal["streamable-http"] = "streamable-http"
    url: str = Field(..., min_length=1)
    headers: dict[str, str] | None = None

    @model_validator(mode="before")
    @classmethod
    def validate_no_stdio_fields(cls, data: object) -> object:
        if isinstance(data, dict):
            forbidden = {"command", "args", "env", "cwd"}
            found = forbidden.intersection(data.keys())
            if found:
                raise ValueError(
                    f"streamable-http transport must not contain stdio fields: {', '.join(sorted(found))}"
                )
        return data


McpServerUnion = McpStdioServer | McpSseServer | McpStreamableHttpServer


class McpSettings(BaseModel):
    mcpServers: dict[str, McpServerUnion] = Field(default_factory=dict)


class McpRegistryEntry(BaseModel):
    name: str
    description: str
    repository: str | None = None
    package: str | None = None
    agent_configs: dict[str, McpServerUnion] = Field(default_factory=dict)
    default_config: McpServerUnion | None = None
