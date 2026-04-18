import pytest

from deps_file_storage.auth import (
    _is_user_has_one_organisation,
    _validate_user_organisation,
)
from deps_file_storage.exceptions import AuthError


def test__is_user_has_one_organisation__positive(valid_decoded_token):
    expected = True
    test_output = _is_user_has_one_organisation(valid_decoded_token)

    assert expected == test_output


def test__is_user_has_one_organisation__negative(invalid_decoded_token):
    expected = False
    test_output = _is_user_has_one_organisation(invalid_decoded_token)

    assert expected == test_output


def test__validate_user_organisation__positive(valid_decoded_token):
    _validate_user_organisation(valid_decoded_token)


def test__validate_user_organisation__negative(invalid_decoded_token):
    with pytest.raises(AuthError):
        _validate_user_organisation(invalid_decoded_token)
