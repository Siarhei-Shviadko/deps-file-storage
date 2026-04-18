import os
from http import HTTPStatus
from io import BytesIO

import pytest


class TestFileStorage:
    base_url = "/api/storage/v1/file"

    pdf_filename = "sample.pdf"
    jpg_filename = "sample.jpg"
    png_filename = "sample.png"
    eml_filename = "sample.eml"
    msg_filename = "sample.msg"

    fake_pdf_filename = "fake.pdf"
    fake_jpg_filename = "fake.jpg"
    fake_png_filename = "fake.png"
    fake_eml_filename = "fake.eml"
    fake_msg_filename = "fake.msg"

    default_filename = pdf_filename

    def test_upload__valid_data__return_ok(self, client):
        res = self._upload_file(client, self.default_filename)

        assert res.status_code == HTTPStatus.OK

    def test_upload__valid_data__return_filename(self, client):
        res = self._upload_file(client, self.default_filename)

        assert res.json()["path"] == self.default_filename

    def test_upload__file_inside_non_existing_directory__return_filename(self, client):
        path = "foo/bar"
        res = self._upload_file(client, self.default_filename, path=path)

        assert res.json()["path"] == path + "/" + self.default_filename

    def test_upload__already_existing_file__return_conflict(self, client):
        self._upload_file(client, self.default_filename)

        res = self._upload_file(client, self.default_filename)

        assert res.status_code == HTTPStatus.CONFLICT

    def test_download__existing_file__return_ok(self, client):
        path = self._upload_file(client, self.default_filename).json()["path"]

        res = self._download_file(client, path)

        assert res.status_code == HTTPStatus.OK

    def test_download__existing_file__return_valid_data(self, client):
        path = self._upload_file(client, self.default_filename).json()["path"]

        res = self._download_file(client, path)

        assert res.content == self._get_file(self.default_filename).read()

    def test_download__not_existing_file__return_not_found(self, client):
        res = self._download_file(client, "foo")

        assert res.status_code == HTTPStatus.NOT_FOUND

    def test_delete__existing_doc__return_ok(self, client):
        path = self._upload_file(client, self.default_filename).json()["path"]

        res = self._delete_file(client, path)

        assert res.status_code == HTTPStatus.NO_CONTENT

    def test_delete__not_existing_doc__return_not_found(self, client):
        res = self._delete_file(client, "foo")

        assert res.status_code == HTTPStatus.NOT_FOUND

    def test_delete__folder__return_not_found(self, client):
        path = "foo/bar"
        self._upload_file(client, self.default_filename, path=path)

        res = self._delete_file(client, "foo")

        assert res.status_code == HTTPStatus.NOT_FOUND

    @pytest.mark.parametrize(
        "filename",
        [pdf_filename, png_filename, jpg_filename, eml_filename, msg_filename],
    )
    def test_upload__checking_valid_mimetype__return_ok(self, client, filename):
        res = self._upload_file(client, filename)

        assert res.status_code == HTTPStatus.OK

    @pytest.mark.skip("Temporary remove mimetype checking")
    @pytest.mark.parametrize(
        "filename",
        [
            fake_pdf_filename,
            fake_png_filename,
            fake_jpg_filename,
            fake_eml_filename,
            fake_msg_filename,
        ],
    )
    def test_upload__checking_invalid_mimetype__return_bad_request(self, client, filename):
        res = self._upload_file(client, filename)

        assert res.status_code == HTTPStatus.UNSUPPORTED_MEDIA_TYPE

    def _upload_file(self, client, filename, path=None):
        base_url = self.base_url
        if path is not None:
            base_url = base_url + "/" + path
        return client.post(base_url, files={"file": (filename, self._get_file(filename))})

    def _download_file(self, client, path):
        return client.get(self.base_url + "/" + path)

    def _delete_file(self, client, path):
        return client.delete(self.base_url + "/" + path)

    @staticmethod
    def _get_file(filename):
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.join("../data", filename))
        with open(file_path, "rb") as f:
            data = f.read()

        return BytesIO(data)
