
def scope_to_environ(scope: dict):
    headers = {}
    for i in scope.get('headers', []):
        headers[i[0].decode().lower()] = i[1].decode()

    return {
        'REQUEST_METHOD': scope.get('method', 'GET'),
        'QUERY_STRING': scope.get('query_string', b'').decode(),
        'CONTENT_TYPE': headers.get('content-type'),
        'CONTENT_LENGTH': headers.get('content-length')
    }

