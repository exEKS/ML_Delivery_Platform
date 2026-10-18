import pytest
from platform_contracts.model_spec import ModelSpec
from pydantic import ValidationError


def test_minimal_model_spec_is_valid() -> None:
    raw_spec = {
        "apiVersion": "mlplatform.io/v1",
        "kind": "Model",
        "metadata": {"name": "credit-default", "owner": "portfolio-user"},
    }

    spec = ModelSpec.model_validate(raw_spec)
    assert spec.api_version == "mlplatform.io/v1"
    assert spec.kind == "Model"
    assert spec.metadata.name == "credit-default"
    assert spec.metadata.owner == "portfolio-user"


def test_wrong_kind_is_rejected() -> None:
    raw_spec = {
        "apiVersion": "mlplatform.io/v1",
        "kind": "model",
        "metadata": {"name": "credit_default", "owner": "portfolio_user"},
    }

    with pytest.raises(ValidationError) as exc_info:
        ModelSpec.model_validate(raw_spec)

    error = exc_info.value.errors()[0]

    assert error["loc"] == ("kind",)
    assert error["type"] == "literal_error"


def test_unknown_metadata_field_is_rejected() -> None:
    raw_spec = {
        "apiVersion": "mlplatform.io/v1",
        "kind": "Model",
        "metadata": {
            "name": "credit_default",
            "owner": "portfolio_user",
            "unknown": 123,
        },
    }

    with pytest.raises(ValidationError) as exc_info:
        ModelSpec.model_validate(raw_spec)

    error = exc_info.value.errors()[0]

    assert error["loc"] == ("metadata", "unknown")
    assert error["type"] == "extra_forbidden"


def test_owner_with_wrong_type_is_rejected() -> None:
    raw_spec = {
        "apiVersion": "mlplatform.io/v1",
        "kind": "Model",
        "metadata": {"name": "credit-default", "owner": 123},
    }
    with pytest.raises(ValidationError) as exc_info:
        ModelSpec.model_validate(raw_spec)

    error = exc_info.value.errors()[0]

    assert error["loc"] == ("metadata", "owner")
    assert error["type"] == "string_type"


def test_empty_owner_is_rejected() -> None:
    raw_spec = {
        "apiVersion": "mlplatform.io/v1",
        "kind": "Model",
        "metadata": {"name": "credit-default", "owner": ""},
    }

    with pytest.raises(ValidationError) as exc_info:
        ModelSpec.model_validate(raw_spec)

    error = exc_info.value.errors()[0]

    assert error["loc"] == ("metadata", "owner")
    assert error["type"] == "string_too_short"
