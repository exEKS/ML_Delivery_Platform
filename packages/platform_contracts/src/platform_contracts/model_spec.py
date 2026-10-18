from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ModelMetadata(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
    )

    name: str
    owner: str = Field(min_length=1)


class ModelSpec(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    api_version: Literal["mlplatform.io/v1"] = Field(alias="apiVersion")
    kind: Literal["Model"]
    metadata: ModelMetadata
