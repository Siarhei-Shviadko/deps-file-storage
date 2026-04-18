from deps_file_storage.api.utils.headers import get_download_headers

correct_mimetype_headers_expected_dict = {
    "Content-Disposition": f'attachment; filename="file.json"',
    "Content-Type": "application/json",
}

incorrect_mimetype_headers_expected_dict = {
    "Content-Disposition": f'attachment; filename="file.wrong_type"',
}


def test__get_download_headers__correct_mime_type():
    correct_mimetype_file = "file.json"
    result = get_download_headers(correct_mimetype_file)
    assert result == correct_mimetype_headers_expected_dict


def test__get_download_headers__incorrect_mime_type():
    incorrect_mimetype_file = "file.wrong_type"
    result = get_download_headers(incorrect_mimetype_file)
    assert result == incorrect_mimetype_headers_expected_dict
