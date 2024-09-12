import base64
from datetime import datetime
import http.client
import json

import pytest
import requests

"""NOTE: The tests in this file start off with a happy path and get progressively more complex to
showcase what ResponderAPI is capable of. Do not be alarmed if initial tests seem to produce
non-standard compliant responses. You can make them conform to HTTP standards as show in the more
complex requests below.
"""

# This will be the URL ot the IP address of the host running ResponderAPI
SERVER_HOST = "remotehost:8080"
# Out of the box, ResponderAPI supports HTTP. If you want to test with HTTPS, set up an HTTPS
# proxy and point it to the host running ResponderAPI
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
    """A simple GET request for / with the default response.
       No query string params given. Empty request body.
    """
    expected_http_status_code = 200

    resp = requests.get(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/")
    assert resp.status_code == expected_http_status_code

    assert len(resp.text) > 0
    resp_body = json.loads(resp.text)

    assert resp_body.get("protocol") == REQUEST_PROTOCOL_VERSION
    assert resp_body.get("method") == "GET"

    assert isinstance(resp_body.get("user_agent"), str) is True
    assert len(resp_body.get("user_agent")) > 0

    assert isinstance(resp_body.get("client_address"), str) is True
    assert len(resp_body.get("client_address")) > 0
    assert resp_body.get("host") == f"{SERVER_HOST}"
    assert resp_body.get("url_path") == "/"

    assert isinstance(resp_body.get("content_type"), str) is True
    assert len(resp_body.get("content_type")) == 0

    assert resp_body.get("content_length") == 0
    assert len(resp_body.get("request_body")) == 0
    assert resp_body.get("request_body") == ''
    assert resp_body.get("found_headers") == None
    assert resp_body.get("params") == {"random_delay": {}}

    assert isinstance(resp_body.get("responderapi_id"), str) is True
    assert len(resp_body.get("responderapi_id")) > 0

    assert isinstance(resp_body.get("called_at"), str) is True
    assert len(resp_body.get("called_at")) > 0
    assert resp_body.get("called_at") < f"{datetime.now().isoformat()}Z"

    assert isinstance(resp_body.get("execution_time"), str) is True
    assert len(resp_body.get("execution_time")) > 0


def test_request_protocol():
    """A simple GET request for / with the default response.
       Tests for the HTTP protocol NOT being one or more unwanted ones.
       No query string params given. Empty request body.
    """
    resp = requests.get(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/")
    resp_body = json.loads(resp.text)

    assert resp_body.get("protocol") not in ["NOT_REALLY_HTTP/2.0", "nOiDeA/3.5"]


def test_request_method():
    """A barebones POST request for / with the default response.
       No query string params given. Request has no body.
    """
    resp = requests.post(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/")

    assert len(resp.text) > 0
    resp_body = json.loads(resp.text)

    assert resp_body.get("method") == "POST"


def test_request_user_agent():
    """A simple GET request for / with the default response.
       No query string params given. Empty request body.
    """
    user_agent = "Just Mocking it/1.9"
    headers = { "User-Agent": user_agent }

    resp = requests.get(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/", headers=headers)

    assert len(resp.text) > 0
    resp_body = json.loads(resp.text)

    assert isinstance(resp_body.get("user_agent"), str) is True
    assert resp_body.get("user_agent") == user_agent


def test_request_client_address():
    """A simple GET request for / with the default response.
       No query string params given. Empty request body.
    """
    resp = requests.get(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/")

    assert len(resp.text) > 0
    resp_body = json.loads(resp.text)

    assert isinstance(resp_body.get("client_address"), str) is True


def test_request_host():
    """A simple GET request for / with the default response.
       No query string params given. Empty request body.
    """
    resp = requests.get(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/")

    assert len(resp.text) > 0
    resp_body = json.loads(resp.text)

    assert resp_body.get("host") == f"{SERVER_HOST}"


def test_request_url_path():
    """A simple GET request for /any/url/you/want with the default response.
       No query string params given. Empty request body.
    """
    resp = requests.get(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/any/url/you/want")

    assert len(resp.text) > 0
    resp_body = json.loads(resp.text)

    assert resp_body.get("url_path") == "/any/url/you/want"


def test_request_post_has_content_type():
    """A simple POST request for / with the default response.
       No query string params given. Request has a JSON body.
       Request Content-Type set to application/json
    """
    content_type = "application/json"
    headers = { "Content-Type": content_type }
    request_body = json.dumps({"payload": "Request body"})

    resp = requests.post(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/", headers=headers, data=request_body)

    assert len(resp.text) > 0
    resp_body = json.loads(resp.text)

    assert resp_body.get("method") == "POST"
    assert isinstance(resp_body.get("content_type"), str) is True
    assert resp_body.get("content_type") == content_type


def test_request_post_has_content_length():
    """A simple POST request for / with the default response.
       No query string params given. Request has a JSON body.
       Request Content-Type set to application/json
    """
    content_type = "application/json"
    headers = { "Content-Type": content_type }
    request_body = json.dumps({"payload": "Request body"})

    resp = requests.post(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/", headers=headers, data=request_body)

    assert len(resp.text) > 0
    resp_body = json.loads(resp.text)

    assert resp_body.get("content_length") == 27


def test_request_post_has_body():
    """A simple POST request for / with the default response.
       No query string params given. Request has a JSON body.
    """
    request_body = json.dumps({"payload": "Request body"})

    resp = requests.post(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/", data=request_body)

    assert len(resp.text) > 0
    resp_body = json.loads(resp.text)

    assert resp_body.get("method") == "POST"
    assert resp_body.get("content_length") == 27
    assert len(resp_body.get("request_body")) == 36
    assert resp_body.get("request_body") == "eyJwYXlsb2FkIjogIlJlcXVlc3QgYm9keSJ9"


def test_request_get_has_params():
    """A simple GET request for / with the default response.
       No query string params given. Request has no body.
    """
    resp = requests.get(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/")

    assert len(resp.text) > 0
    resp_body = json.loads(resp.text)

    assert "params" in resp_body


def test_request_get_has_expected_headers():
    """A simple GET request for / with the default response.
       No query string params given. Request has no body.
    """
    headers = {
        "Custom-Header": "2024SEP01",
        "Some-Other-Header":
        "Anything", "Content-Type": "application/example"
    }
    resp = requests.get(
        f"{REQUEST_PROTOCOL}://{SERVER_HOST}/?expected_headers=Q3VzdG9tLUhlYWRlcg==,U29tZS1PdGhlci1IZWFkZXI=,Q29udGVudC1UeXBl",
        headers=headers
    )

    assert len(resp.text) > 0
    resp_body = json.loads(resp.text)

    assert "Custom-Header" in resp_body.get("params").get("expected_headers")
    assert "Some-Other-Header" in resp_body.get("params").get("expected_headers")
    assert "Content-Type" in resp_body.get("params").get("expected_headers")


def test_request_get_response_has_found_headers():
    """A simple GET request for / with the default response.
       No query string params given. Request has no body.
    """
    headers = {
        "Custom-Header": "2024SEP01",
        "Some-Other-Header": "Anything",
        "Content-Type": "application/example"
    }
    resp = requests.get(
        f"{REQUEST_PROTOCOL}://{SERVER_HOST}/?expected_headers=Q3VzdG9tLUhlYWRlcg==,U29tZS1PdGhlci1IZWFkZXI=",
        headers=headers
    )

    assert len(resp.text) > 0
    resp_body = json.loads(resp.text)

    assert "Custom-Header: 2024SEP01" in resp_body.get("found_headers")
    assert "Some-Other-Header: Anything" in resp_body.get("found_headers")
    assert "Content-Type" not in resp_body.get("found_headers")


def test_request_get_response_has_request_body():
    """A simple POST request for / with the default response.
       No query string params given. Request has body.
    """
    expected_http_status_code = 200
    request_body = json.dumps({"payload": "Request body"})

    resp = requests.post(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/", data=request_body)
    assert resp.status_code == expected_http_status_code
    assert len(resp.text) > 0

    resp_body = json.loads(resp.text)
    assert resp_body.get("protocol") == REQUEST_PROTOCOL_VERSION
    assert resp_body.get("method") == "POST"

    assert resp_body.get("content_length") == 27
    assert len(resp_body.get("request_body")) == 36
    assert resp_body.get("request_body") == "eyJwYXlsb2FkIjogIlJlcXVlc3QgYm9keSJ9"


def test_request_get_response_has_responderapi_id():
    """A simple GET request for / with the default response.
       No query string params given. Request has no body.
    """
    resp = requests.get(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/")

    assert len(resp.text) > 0
    resp_body = json.loads(resp.text)

    assert isinstance(resp_body.get("responderapi_id"), str) is True
    assert len(resp_body.get("responderapi_id")) > 0


def test_request_get_response_has_called_at():
    """A simple GET request for / with the default response.
       No query string params given. Request has no body.
    """
    resp = requests.get(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/")

    assert len(resp.text) > 0
    resp_body = json.loads(resp.text)

    assert isinstance(resp_body.get("called_at"), str) is True
    assert len(resp_body.get("called_at")) > 0
    assert resp_body.get("called_at") < f"{datetime.now().isoformat()}Z"


def test_request_get_response_has_execution_time():
    """A simple GET request for / with the default response.
       No query string params given. Request has no body.
    """
    resp = requests.get(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/")

    assert len(resp.text) > 0
    resp_body = json.loads(resp.text)

    assert isinstance(resp_body.get("execution_time"), str) is True
    assert len(resp_body.get("execution_time")) > 0


# ----------------------------------------------------------------
# Testing request query params
# ----------------------------------------------------------------


def test_set_response_http_status_code():
    """A simple GET request for / with a custom response status code of 400 Bad Request.
       No query string params given. Empty request body.
    """
    expected_http_status_code = 400

    query_string = f"status_code={expected_http_status_code}"
    resp = requests.get(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/?{query_string}")
    assert resp.status_code == expected_http_status_code
    resp_body = json.loads(resp.text)
    assert resp_body["url_path"] == f"/?status_code={expected_http_status_code}"
    assert resp_body.get("params").get("status_code") == expected_http_status_code


def test_http_request_url_path():
    """A GET request for /blog/post/20240616/post1.html?status_code=402 i.e a GET request for
    /blog/post/20240616/post1.html with a custom HTTP response status code
    """
    expected_http_status_code = 402
    resp = requests.get(
        f"{REQUEST_PROTOCOL}://{SERVER_HOST}/blog/post/20240616/post1.html?status_code={expected_http_status_code}"
    )
    assert resp.status_code == expected_http_status_code
    assert len(resp.text) > 0
    resp_body = json.loads(resp.text)
    assert resp_body["params"]["status_code"] == expected_http_status_code
    assert resp_body["url_path"] == f"/blog/post/20240616/post1.html?status_code={expected_http_status_code}"


def test_set_http_response_delay():
    """A GET request for /?delay=100 i.e. a GET request for / with the response delayed by 100ms
    """
    delay = 100
    resp = requests.get(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/?delay={delay}")
    assert len(resp.text) > 0
    resp_body = json.loads(resp.text)
    assert resp_body["url_path"] == f"/?delay={delay}"
    assert resp_body.get("params").get("delay") == delay


def test_set_http_response_random_delay():
    """A GET request for /?random_delay=100,200 i.e. a GET request for / with the response delayed by
    between 100ms and 200ms
    """
    min_delay = 100
    max_delay = 200
    resp = requests.get(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/?random_delay={min_delay},{max_delay}")
    assert len(resp.text) > 0
    resp_body = json.loads(resp.text)
    assert resp_body["url_path"] == f"/?random_delay={min_delay},{max_delay}"
    assert resp_body.get("params").get("random_delay").get("min") == min_delay
    assert resp_body.get("params").get("random_delay").get("max") == max_delay


def test_set_http_response_no_body():
    """A GET request for /?no_body i.e. a GET request for / with an empty response body
    """
    resp = requests.get(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/?no_body")
    assert len(resp.text) == 0


def test_set_http_response_no_headers():
    """A GET request for /?no_headers i.e. a GET request for / with a response with no headers
    """
    headers_dict = {
        "Allow": "OPTIONS, GET, HEAD, POST",
        "Cache-Control": "max-age=604800",
        "Server": "ResponderAPI 2024-003"
    }
    headers_list = headers_d2l(headers_dict)
    headers = ",".join(headers_list)
    resp = requests.get(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/?no_headers&no_body&headers={headers}")
    assert "Allow" not in resp.headers
    assert "Cache-Control" not in resp.headers
    assert "Server" not in resp.headers


def test_http_request_delete_method():
    """ response "method" == "DELETE"
    """
    resp = requests.delete(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/")
    resp_body = json.loads(resp.text)
    assert resp_body["method"] == "DELETE"


def test_http_request_get_method():
    """ response "method" == "GET"
    """
    resp = requests.get(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/")
    resp_body = json.loads(resp.text)
    assert resp_body["method"] == "GET"


def test_http_request_options_method():
    """ response "method" == "OPTIONS"
    """
    resp = requests.options(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/")
    resp_body = json.loads(resp.text)
    assert resp_body["method"] == "OPTIONS"


def test_http_request_post_method():
    """ response "method" == "POST"
    """
    resp = requests.post(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/")
    resp_body = json.loads(resp.text)
    assert resp_body["method"] == "POST"


def test_http_request_patch_method():
    """ response "method" == "PATCH"
    """
    resp = requests.patch(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/")
    resp_body = json.loads(resp.text)
    assert resp_body["method"] == "PATCH"


def test_http_request_server_host():
    """ response has no "host"
    """
    resp = requests.get(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/")
    resp_body = json.loads(resp.text)
    assert resp_body["host"] == SERVER_HOST


def test_http_request_user_agent():
    """ response has no "user_agent"
    """
    resp = requests.get(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/")
    resp_body = json.loads(resp.text)
    assert resp_body["user_agent"].startswith("python-requests/") == True


def test_http_request_empty_content_type():
    """ response has no "content_type"
    """
    resp = requests.get(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/")
    resp_body = json.loads(resp.text)
    assert len(resp_body["content_type"]) == 0


def test_http_request_no_headers():
    """ {"params": {}} has no "headers"
    """
    resp = requests.get(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/")
    resp_body = json.loads(resp.text)
    assert resp_body.get("params").get("headers") == None


def test_http_request_delay():
    """ `delay`
    """
    resp = requests.get(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/")
    resp_body = json.loads(resp.text)
    assert resp_body.get("params").get("delay") == None


def test_http_request_random_delay():
    """ `random_delay`
    """
    resp = requests.get(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/")
    resp_body = json.loads(resp.text)
    assert resp_body.get("params").get("random_delay") == {}


def test_http_request_params():
    """ response "params" == {"random_delay": {}}
    """
    resp = requests.get(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/")
    resp_body = json.loads(resp.text)
    assert resp_body.get("params") == {"random_delay": {}}


def test_http_request_called_at():
    """ response "called_at" == "2024-09-11T15:51:05.809722Z" (or similar)
    """
    resp = requests.get(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/")
    resp_body = json.loads(resp.text)
    assert resp_body["called_at"] < f"{datetime.now().isoformat()}Z"


def test_http_request_responder_id():
    """ response "responderapi_id" == a7988984-7055-11ef-899a-1ec32bd4abd4" (or similar)
    """
    resp = requests.get(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/")
    resp_body = json.loads(resp.text)
    assert resp_body.get("responder_id") is not ""


# ----------------------------------------------------------------
# Sample HTTP requests
# ----------------------------------------------------------------

# CONNECT

def test_http_connect_response():
    """Test response to an CONNECT request equivalent to the following curl request:

    $ curl -vvv -X CONNECT 'remotehost:8080?no_body&no_headers'

    Request:

    > CONNECT /?no_body&no_headers HTTP/1.1
    > Host: remotehost:8080
    > User-Agent: curl/8.4.0
    > Accept: */*

    Response:

    < HTTP/1.1 200 OK
    < Date: Wed, 04 Sep 2024 11:57:23 GMT
    < Content-Length: 0

    source: https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/CONNECT
    """

    status_code = 200
    no_headers = "no_headers"
    no_body = "no_body"
    query_string = f"status_code={status_code}&{no_headers}&{no_body}"
    host = f"{SERVER_HOST}"
    conn = http.client.HTTPConnection(host)
    conn.request("CONNECT", f"/blog/page/123456?{query_string}", headers={"Host": host})
    resp = conn.getresponse()
    resp_status_code = resp.status
    resp_headers = resp.headers
    resp_body = resp.read()
    conn.close()
    assert resp_status_code == status_code
    assert len(resp_body) == 0
    assert len(resp_headers.get("Date")) > 0
    assert isinstance(resp_headers.get("Date"), str) is True
    assert resp_headers["Content-Length"] == "0"

# DELETE

def test_http_delete_response():
    """Test response to an DELETE request equivalent to the following curl request:

    $ curl -vvv -X DELETE 'remotehost:8080/blog/page/143285?status_code=204&no_body'

    Request:

    > DELETE /blog/page/143285?status_code=204&no_body HTTP/1.1
    > Host: remotehost:8080
    > User-Agent: curl/8.4.0
    > Accept: */*

    Response:

    < HTTP/1.1 204 No Content
    < Date: Wed, 04 Sep 2024 12:34:05 GMT

    source: https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/DELETE
    """

    status_code = 204
    no_body = "no_body"
    query_string = f"status_code={status_code}&{no_body}"
    resp = requests.delete(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/blog/page/143285?{query_string}")

    assert resp.status_code == status_code
    assert len(resp.text) == 0
    assert len(resp.headers.get("Date")) > 0
    assert isinstance(resp.headers.get("Date"), str) is True

# GET

def test_http_get_response():
    """Test response to an GET request equivalent to the following curl request:

    $ curl -vvv 'remotehost:8080/blog/page/143285?status_code=200&headers=Q29udGVudC1UeXBlOiBhcHBsaWNhdGlvbi9qc29u&body=eyJ0aXRsZSI6ICJUZXN0IFBhZ2UiLCAiYm9keSI6ICJMb3JlbSBpcHN1bSJ9'

    Request:

    > GET /blog/page/143285?status_code=200&headers=Q29udGVudC1UeXBlOiBhcHBsaWNhdGlvbi9qc29u&body=eyJ0aXRsZSI6ICJUZXN0IFBhZ2UiLCAiYm9keSI6ICJMb3JlbSBpcHN1bSJ9 HTTP/1.1
    > Host: remotehost:8080
    > User-Agent: curl/8.4.0
    > Accept: */*

    Response:

    < HTTP/1.1 200 OK
    < Content-Type: application/json
    < Date: Wed, 04 Sep 2024 17:30:21 GMT
    < Content-Length: 414

    source: https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/GET
    """

    status_code = 200
    headers_dict = {
        "Content-Type": "application/json",
    }
    headers_list = headers_d2l(headers_dict)
    headers = ",".join(headers_list)

    body_dict = {
        "title": "Test Page",
        "body": "Lorem ipsum"
    }
    body_str = json.dumps(body_dict)
    body = base64.b64encode(body_str.encode("utf-8")).decode("utf-8")
    query_string = f"status_code={status_code}&headers={headers}&body={body}"
    resp = requests.get(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/blog/page/143285?{query_string}")

    assert resp.status_code == status_code
    assert resp.headers["Content-Type"] == headers_dict["Content-Type"]
    assert len(resp.text) > 0
    assert int(resp.headers["Content-Length"]) > 0
    resp_content = json.loads(resp.text)
    for k in resp_content:
        assert resp_content[k] == body_dict[k]

# HEAD

def test_http_head_response():
    """Test response to an HEAD request equivalent to the following curl request:

    $ curl -vvv -X HEAD 'remotehost:8080/blog/page/143285?status_code=200'

    NOTE: if you use curl's -X HEAD option, curl will hang forever. This is a feature of curl, it hangs because it
    expects to receive a Content-Length: 0 header, which is not provided when ResponderAPI returns a zero-length body.
    If you want to make curl exit immediately, replace -X HEAD with --head or instruct ResponderAPI to add
    Content-Length: 0 header, as in

    $ curl -vvv -X HEAD 'remotehost:8080/blog/page/143285?status_code=200&no_body&headers=Q29udGVudC1MZW5ndGg6IDA='

    Request:

    > HEAD /blog/page/143285?status_code=200&no_body HTTP/1.1
    > Host: remotehost:8080
    > User-Agent: curl/8.4.0
    > Accept: */*

    Response:

    < HTTP/1.1 200 OK
    < Content-Type: application/json
    < Date: Wed, 04 Sep 2024 18:19:43 GMT

    source: https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/GET
    """

    status_code = 200
    query_string = f"status_code={status_code}"

    # Uncomment the following section, if you want to instruct ResponderAPI to add Content-Length: 0 header
    #
    #     headers_dict = {
    #         "Content-Length": 0,
    #     }
    #     headers_list = [
    #         base64.b64encode(f"{i}: {headers_dict[i]}".encode("utf-8")).decode("utf-8")
    #         for i in headers_dict
    #     ]
    #     headers = ",".join(headers_list)
    #     query_string = f"status_code={status_code}&headers={headers}"

    resp = requests.head(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/blog/page/143285?{query_string}")

    assert resp.status_code == status_code
    assert len(resp.text) == 0

# OPTIONS

def test_http_options_response():
    """Test response to an OPTIONS request equivalent to the following curl request:

    $ curl -vvv -X OPTIONS 'remotehost:8080/page/143285?status_code=204&headers=QWxsb3c6IE9QVElPTlMsIEdFVCwgSEVBRCwgUE9TVA==,Q2FjaGUtQ29udHJvbDogbWF4LWFnZT02MDQ4MDA=,U2VydmVyOiBSZXNwb25kZXJBUEkgMjAyNC0wMDM=&no_body'

    Request:

    > OPTIONS /page/143285?status_code=204&headers=QWxsb3c6IE9QVElPTlMsIEdFVCwgSEVBRCwgUE9TVA==,Q2FjaGUtQ29udHJvbDogbWF4LWFnZT02MDQ4MDA=,U2VydmVyOiBSZXNwb25kZXJBUEkgMjAyNC0wMDM=&no_body HTTP/1.1
    > Host: remotehost:8080
    > User-Agent: curl/8.4.0
    > Accept: */*

    Response:

    < HTTP/1.1 204 No Content
    < Allow: OPTIONS, GET, HEAD, POST
    < Cache-Control: max-age=604800
    < Server: ResponderAPI (01/01)
    < Date: Tue, 03 Sep 2024 22:46:00 GMT

    source: https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/OPTIONS
    """

    status_code = 204
    headers_dict = {
        "Allow": "OPTIONS, GET, HEAD, POST",
        "Cache-Control": "max-age=604800",
        "Server": "ResponderAPI 2024-003"
    }
    headers_list = headers_d2l(headers_dict)
    headers = ",".join(headers_list)
    no_body = "no_body"
    query_string = f"status_code={status_code}&headers={headers}&{no_body}"
    resp = requests.options(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/blog/page/143285?{query_string}")

    assert len(resp.text) == 0
    assert resp.headers["Allow"] == headers_dict["Allow"]
    assert resp.headers["Cache-Control"] == headers_dict["Cache-Control"]
    assert resp.headers["Server"] == headers_dict["Server"]

# PATCH

def test_http_patch_response():
    """Test response to an PATCH request equivalent to the following curl request:

    $ curl -vvv -X PATCH 'remotehost:8080/blog/page/143285?status_code=204&headers=Q29udGVudC1UeXBlOiBhcHBsaWNhdGlvbi9leGFtcGxl,SWYtTWF0Y2g6IGUwMDIzYWE0ZQ==&no_body' -d '{"id": "1234567890", "add": "nickname": "Chief"}'
    Request:

    > PATCH /blog/page/143285?status_code=204&headers=Q29udGVudC1UeXBlOiBhcHBsaWNhdGlvbi9leGFtcGxl,SWYtTWF0Y2g6IGUwMDIzYWE0ZQ==&no_body HTTP/1.1
    > Host: remotehost:8080
    > User-Agent: curl/8.4.0
    > Accept: */*
    > Content-Length: 68
    > Content-Type: application/x-www-form-urlencoded

    Response:

    < HTTP/1.1 204 No Content
    < Content-Type: application/example
    < If-Match: e0023aa4e
    < Date: Sat, 07 Sep 2024 22:35:41 GMT

    source: https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/PATCH
    """

    status_code = 204
    headers_dict = {
        "Content-Type": "application/example",
        "If-Match": "e0023aa4e",
    }
    headers_list = headers_d2l(headers_dict)
    headers = ",".join(headers_list)
    no_body = "no_body"
    query_string = f"status_code={status_code}&headers={headers}&{no_body}"
    request_dict = {
        "id": "143285",
        "add": {
            "nickname": "Chief"
        }
    }
    request_body = json.dumps(request_dict)
    resp = requests.patch(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/blog/page/143285?{query_string}", data=request_body)

    assert len(resp.text) == 0
    assert resp.headers["Content-Type"] == headers_dict["Content-Type"]
    assert resp.headers["If-Match"] == headers_dict["If-Match"]

# POST

def test_http_post_response():
    """Test response to an POST request equivalent to the following curl request:

    $ curl -vvv -X POST 'remotehost:8080/blog/page?status_code=201&headers=QWxsb3c6IE9QVElPTlMsIEdFVCwgSEVBRCwgUE9TVA==,Q2FjaGUtQ29udHJvbDogbWF4LWFnZT02MDQ4MDA=,U2VydmVyOiBSZXNwb25kZXJBUEkgKDAxLzAxKQ=='

    Request:

    > POST /blog/page?status_code=201&headers=Q29udGVudC1UeXBlOiBhcHBsaWNhdGlvbi9qc29u&body=eyJpZCI6ICIxNDMyODUifQ== HTTP/1.1
    > Host: remotehost:8080
    > User-Agent: curl/8.4.0
    > Accept: */*
    > Content-Length: 49
    > Content-Type: application/x-www-form-urlencoded

    Response:

    < HTTP/1.1 201 Created
    < Content-Type: application/json
    < Date: Sun, 08 Sep 2024 17:48:46 GMT
    < Content-Length: 16

    source: https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/POST
    """

    status_code = 201
    headers_dict = {
        "Content-Type": "application/json",
    }
    headers_list = headers_d2l(headers_dict)
    headers = ",".join(headers_list)
    response_body_dict = {"id": "143285"}
    response_body_str = json.dumps(response_body_dict)
    response_body = base64.b64encode(response_body_str.encode("utf-8")).decode("utf-8")
    query_string = f"status_code={status_code}&headers={headers}&body={response_body}"
    request_dict = {
        "employee": {
            "name": "Mark",
            "job": "Rockstar"
        }
    }
    request_body = json.dumps(request_dict)
    resp = requests.post(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/blog/page?{query_string}", data=request_body)

    assert resp.headers["Content-Type"] == headers_dict["Content-Type"]
    resp_body = json.loads(resp.text)
    assert resp_body["id"] == response_body_dict["id"]

# PUT

def test_http_put_response():
    """Test response to an PUT request equivalent to the following curl request:

    $ curl -vvv -X PUT 'remotehost:8080/blog/page?status_code=201&headers=Q29udGVudC1UeXBlOiBhcHBsaWNhdGlvbi9qc29u&no_body' -d '{"employee": {"name": "Paul", "job": "Guru"}}'

    Request:

    > PUT /blog/page?status_code=201&headers=Q29udGVudC1UeXBlOiBhcHBsaWNhdGlvbi9qc29u&no_body HTTP/1.1
    > Host: remotehost:8080
    > User-Agent: curl/8.4.0
    > Accept: */*
    > Content-Length: 45
    > Content-Type: application/x-www-form-urlencoded

    Response:

    < HTTP/1.1 201 Created
    < Content-Type: application/json
    < Date: Sun, 08 Sep 2024 19:39:28 GMT
    < Content-Length: 0

    source: https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/PUT
    """

    status_code = 201
    headers_dict = {
        "Content-Type": "application/json",
    }
    headers_list = headers_d2l(headers_dict)
    headers = ",".join(headers_list)
    query_string = f"status_code={status_code}&headers={headers}&no_body"
    request_dict = {
        "employee": {
            "name": "Paul",
            "job": "Guru"
        }
    }
    request_body = json.dumps(request_dict)
    resp = requests.put(f"{REQUEST_PROTOCOL}://{SERVER_HOST}/blog/page?{query_string}", data=request_body)

    assert resp.headers["Content-Type"] == headers_dict["Content-Type"]
    assert len(resp.text) == 0

# TRACE

def test_http_trace_response():
    """Test response to an TRACE request equivalent to the following curl request:

    $ curl -vvv -X TRACE 'remotehost:8080/blog?status_code=204&headers=QWxsb3c6IE9QVElPTlMsIEdFVCwgSEVBRCwgUE9TVA==,Q2FjaGUtQ29udHJvbDogbWF4LWFnZT02MDQ4MDA=,U2VydmVyOiBSZXNwb25kZXJBUEkgKDAxLzAxKQ=='

    Request:

    > TRACE /blog?status_code=204&headers=QWxsb3c6IE9QVElPTlMsIEdFVCwgSEVBRCwgUE9TVA==,Q2FjaGUtQ29udHJvbDogbWF4LWFnZT02MDQ4MDA=,U2VydmVyOiBSZXNwb25kZXJBUEkgKDAxLzAxKQ== HTTP/1.1
    > Host: remotehost:8080
    > User-Agent: curl/8.4.0
    > Accept: */*

    Response:

    < HTTP/1.1 204 No Content
    < Allow: OPTIONS, GET, HEAD, POST
    < Server: ResponderAPI (01/01)
    < Date: Tue, 03 Sep 2024 22:46:00 GMT

    source: https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/OPTIONS
    """

    status_code = 200
    headers_dict = {
        "Via": "1.1 proxy.example.com, 1.1 proxy.example.net",
    }
    headers_list = headers_d2l(headers_dict)
    headers = ",".join(headers_list)
    no_body = "no_body"
    query_string = f"status_code={status_code}&headers={headers}&{no_body}"

    host = f"{SERVER_HOST}"
    conn = http.client.HTTPConnection(host)
    conn.request("TRACE", f"/blog/page/123456?{query_string}", headers={"Host": host})
    resp = conn.getresponse()
    resp_headers = resp.headers
    resp_body = resp.read()
    conn.close()
    assert resp_headers["Via"] == headers_dict["Via"]
    assert len(resp_body) == 0
