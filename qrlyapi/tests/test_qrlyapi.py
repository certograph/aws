import base64
import io
import json
import shutil

import pytest
import requests

"""NOTE: The tests in this file start off with a happy path and get progressively more complex to
showcase what QRlyAPI is capable of.
"""

# This will be the URL ot the IP address of the host running QRlyAPI
SERVER_HOST = "remotehost:8080"
# Out of the box, QRlyAPI supports HTTP. If you want to test with HTTPS, set up an HTTPS
# proxy and point it to the host running QRlyAPI
REQUEST_PROTOCOL = "http"
# Some clients may use other versions of the HTTP protocol. If you see failures on assertions
# related to HTTP protocol version, change the value of REQUEST_PROTOCOL_VERSION, unless you
# have a reason to specifically for a mismatch
REQUEST_PROTOCOL_VERSION = "HTTP/1.1"

def headers_d2l(headers_dict: dict) -> list[str]:
    headers_list = [
        base64.b64encode(f"{i}: {headers_dict[i]}".encode("utf-8")).decode("utf-8")
        for i in headers_dict
    ]
    return headers_list

# ----------------------------------------------------------------
# Diagnostic tests
# ----------------------------------------------------------------

def test_default_response():
    """A simple GET request results in a 400 Bad Request response.
       This is expected.
    """
    expected_http_status_code = 400

    resp = requests.get(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/")
    assert resp.status_code == expected_http_status_code
    assert resp.headers["Content-Type"] == "text/plain; charset=utf-8"


def test_minimal():
    """The simplest POST request that returns a QR code PNG image.
    """
    expected_http_status_code = 200
    headers = {"Content-Type": "application/json"}
    data = {"payload": "https://www.certograph.com/"}

    resp = requests.post(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/", headers=headers, data=json.dumps(data), stream=True)
    assert resp.status_code == expected_http_status_code
    assert resp.headers["Content-Type"] == "image/png"

    with open("aws/tests/images/www_certograph_com_29.png", "rb") as file:
        # get response image
        resp_img = io.BytesIO()
        shutil.copyfileobj(resp.raw, resp_img)
        resp_img.seek(0)
        resp_bytes = resp_img.read()
        # get reference image
        ref_img = file.read()

        assert resp_bytes == ref_img


def test_recovery_level():
    """A POST request that returns a QR code PNG image with the given recover level.
    """
    expected_http_status_code = 200
    headers = {"Content-Type": "application/json"}
    data = {"payload": "https://www.certograph.com/", "recovery_level": "highest"}

    resp = requests.post(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/", headers=headers, data=json.dumps(data), stream=True)
    assert resp.status_code == expected_http_status_code
    assert resp.headers["Content-Type"] == "image/png"

    with open("aws/tests/images/www_certograph_com_recovery_level_highest.png", "rb") as file:
        # get response image
        resp_img = io.BytesIO()
        shutil.copyfileobj(resp.raw, resp_img)
        resp_img.seek(0)
        resp_bytes = resp_img.read()

        # get reference image
        ref_img = file.read()

        assert resp_bytes == ref_img

def test_custom_size():
    """A POST request that returns a QR code PNG image with the given width and height.
    """
    expected_http_status_code = 200
    headers = {"Content-Type": "application/json"}
    data = {"payload": "https://www.certograph.com/", "size": 100}

    resp = requests.post(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/", headers=headers, data=json.dumps(data), stream=True)
    assert resp.status_code == expected_http_status_code
    assert resp.headers["Content-Type"] == "image/png"

    with open("aws/tests/images/www_certograph_com_100.png", "rb") as file:
        # get response image
        resp_img = io.BytesIO()
        shutil.copyfileobj(resp.raw, resp_img)
        resp_img.seek(0)
        resp_bytes = resp_img.read()

        # get reference image
        ref_img = file.read()

        assert resp_bytes == ref_img


def test_custom_size_bad_request():
    """A POST request that returns a 400 for invalid size.
    """
    expected_http_status_code = 400
    headers = {"Content-Type": "application/json"}
    data = {"payload": "https://www.certograph.com/", "size": -5}

    resp = requests.post(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/", headers=headers, data=json.dumps(data), stream=True)
    assert resp.status_code == expected_http_status_code
    assert resp.headers["Content-Type"] == "text/plain; charset=utf-8"

def test_foreground_colour():
    """A POST request that returns a QR code PNG image with the given foreground colour.
    """
    expected_http_status_code = 200
    headers = {"Content-Type": "application/json"}
    data = {"payload": "https://www.certograph.com/", "foreground_colour": {"r": 0, "g": 200, "b": 0, "a": 255}}

    resp = requests.post(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/", headers=headers, data=json.dumps(data), stream=True)
    assert resp.status_code == expected_http_status_code
    assert resp.headers["Content-Type"] == "image/png"

    with open("aws/tests/images/www_certograph_com_foreground_colour_0_200_0_255.png", "rb") as file:
        # get response image
        resp_img = io.BytesIO()
        shutil.copyfileobj(resp.raw, resp_img)
        resp_img.seek(0)
        resp_bytes = resp_img.read()

        # get reference image
        ref_img = file.read()

        assert resp_bytes == ref_img

def test_background_colour():
    """A POST request that returns a QR code PNG image with the given background colour.
    """
    expected_http_status_code = 200
    headers = {"Content-Type": "application/json"}
    data = {"payload": "https://www.certograph.com/", "background_colour": {"r": 0, "g": 200, "b": 0, "a": 255}}

    resp = requests.post(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/", headers=headers, data=json.dumps(data), stream=True)
    assert resp.status_code == expected_http_status_code
    assert resp.headers["Content-Type"] == "image/png"

    with open("aws/tests/images/www_certograph_com_background_colour_0_200_0_255.png", "rb") as file:
        # get response image
        resp_img = io.BytesIO()
        shutil.copyfileobj(resp.raw, resp_img)
        resp_img.seek(0)
        resp_bytes = resp_img.read()

        # get reference image
        ref_img = file.read()

        assert resp_bytes == ref_img


def test_background_colour_invalid_r():
    """A POST request that fails for invalid value of R.
    """
    expected_http_status_code = 400
    headers = {"Content-Type": "application/json"}
    data = {"payload": "https://www.certograph.com/", "background_colour": {"r": -200, "g": 200, "b": 0, "a": 255}}

    resp = requests.post(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/", headers=headers, data=json.dumps(data), stream=True)
    assert resp.status_code == expected_http_status_code
    assert resp.headers["Content-Type"] == "text/plain; charset=utf-8"


def test_background_colour_invalid_b():
    """A POST request that fails for invalid value of B.
    """
    expected_http_status_code = 400
    headers = {"Content-Type": "application/json"}
    data = {"payload": "https://www.certograph.com/", "background_colour": {"r": 00, "g": 200, "b": 400, "a": 255}}

    resp = requests.post(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/", headers=headers, data=json.dumps(data), stream=True)
    assert resp.status_code == expected_http_status_code
    assert resp.headers["Content-Type"] == "text/plain; charset=utf-8"


def test_background_colour_missing_a():
    """A POST request that fails for missing value of A.
    """
    expected_http_status_code = 400
    headers = {"Content-Type": "application/json"}
    data = {"payload": "https://www.certograph.com/", "background_colour": {"r": -200, "g": 200, "b": 0}}

    resp = requests.post(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/", headers=headers, data=json.dumps(data), stream=True)
    assert resp.status_code == expected_http_status_code
    assert resp.headers["Content-Type"] == "text/plain; charset=utf-8"

def test_trim_width():
    """A POST request that returns a QR code PNG image with the given trim width.
    """
    expected_http_status_code = 200
    headers = {"Content-Type": "application/json"}
    data = {"payload": "https://www.certograph.com/", "trim_width": 5}

    resp = requests.post(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/", headers=headers, data=json.dumps(data), stream=True)
    assert resp.status_code == expected_http_status_code
    assert resp.headers["Content-Type"] == "image/png"

    with open("aws/tests/images/www_certograph_com_trim_width_5.png", "rb") as file:
        # get response image
        resp_img = io.BytesIO()
        shutil.copyfileobj(resp.raw, resp_img)
        resp_img.seek(0)
        resp_bytes = resp_img.read()

        # get reference image
        ref_img = file.read()

        assert resp_bytes == ref_img


def test_trim_width_bad_request():
    """A POST request that returns a 400 for invalid trim width.
    """
    expected_http_status_code = 400
    headers = {"Content-Type": "application/json"}
    data = {"payload": "https://www.certograph.com/", "trim_width": -5}

    resp = requests.post(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/", headers=headers, data=json.dumps(data), stream=True)
    assert resp.status_code == expected_http_status_code
    assert resp.headers["Content-Type"] == "text/plain; charset=utf-8"


def test_over_max_payload_length():
    """A POST request that returns a 400 for invalid trim width.
    """
    expected_http_status_code = 400
    headers = {"Content-Type": "application/json"}
    data = {"payload": "A" * 4297, "recovery_level": "low"} # 4296 is the maximum number of characters

    resp = requests.post(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/", headers=headers, data=json.dumps(data), stream=True)
    assert resp.status_code == expected_http_status_code
    assert resp.headers["Content-Type"] == "text/plain; charset=utf-8"