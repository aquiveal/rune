from typing import List, Dict, Optional, Literal, Union
from pydantic import BaseModel, Field, model_validator


class McpBase(BaseModel):
    disabled: bool = False
    timeout: int = Field(60, ge=1, le=3600)
    alwaysAllow: Optional[List[str]] = None
    disabledTools: Optional[List[str]] = None
    watchPaths: Optional[List[str]] = None


class McpStdioServer(McpBase):
    type: Literal["stdio"] = "stdio"
    command: str = Field(..., min_length=1)
    args: Optional[List[str]] = None
    env: Optional[Dict[str, str]] = None
    cwd: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def validate_no_http_fields(cls, data: object) -> object:
        if isinstance(data, dict):
            if "url" in data or "headers" in data:
                raise ValueError(
                    "stdio transport must not contain 'url' or 'headers' fields."
                )
        return data


class McpSseServer(McpBase):
    type: Literal["sse"] = "sse"
    url: str = Field(..., min_length=1)
    headers: Optional[Dict[str, str]] = None

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
    headers: Optional[Dict[str, str]] = None

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


McpServerUnion = Union[McpStdioServer, McpSseServer, McpStreamableHttpServer]


class McpSettings(BaseModel):
    mcpServers: Dict[str, McpServerUnion] = Field(default_factory=dict)


class McpRegistryEntry(BaseModel):
    name: str
    description: str
    repository: Optional[str] = None
    package: Optional[str] = None
    agent_configs: Dict[str, McpServerUnion] = Field(default_factory=dict)
    default_config: Optional[McpServerUnion] = None
