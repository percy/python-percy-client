class Error(Exception):
    pass


class AuthError(Error):
    pass


class RepoNotFoundError(Error):
    pass


class UninitializedBuildError(Error):
    pass


class PercyBadRequest(Error):
    """
    HTTP Status code 400
    Example responses:
    {
        "errors": [
            {
                "status": "bad_request"
            }
        ],
        "validation_errors": {
            "base": [
                "The name of each snapshot must be unique, and this name already
                 exists in the build: '/some_path' -- You can fix this by passing
                 a 'name' param when creating the snapshot. See the docs for more
                 info on identifying snapshots for your specific client:
                 https://percy.io/docs"
            ]
        }
    }

    {
        "errors": [
            {
                u'status': u'bad_request',
                u'detail': u'For parallel builds, both parallel_nonce and parallel_total_shards must be given.'
            }
        ]
    }

    """
    def __init__(self, response_json):
        if (
                set(response_json.keys()) == {'errors', 'validation_errors'} and
                set(response_json['validation_errors'].keys()) == {'base'} and
                len(response_json['validation_errors']['base']) == 1):
            error_msg = response_json['validation_errors']['base'][0]
        elif (
                set(response_json.keys()) == {'errors'} and
                len(response_json['errors']) == 1 and
                set(response_json['errors'][0].keys()) == {'status', 'detail'}):
            error_msg = response_json['errors'][0]['detail']
        else:
            error_msg = response_json

        super(PercyBadRequest, self).__init__(error_msg)


class PercyQuotaExceeded(Error):
    """
    HTTP Status code 402
    Example response:
    {
        "errors": [
            {
                "detail": "This repo has exceeded the limits of the free plan. The
                           repository owner (@fotinakis) can visit here to upgrade:
                           https://percy.io/account",
                "status": "quota_exceeded"
            }
        ]
    }
    """
    def __init__(self, response_json):
        if (
                set(response_json.keys()) == {'errors'} and
                len(response_json['errors']) == 1 and
                set(response_json['errors'][0].keys()) == {'detail', 'status'}):
            error_msg = response_json['errors'][0]['detail']
        else:
            error_msg = response_json

        super(PercyQuotaExceeded, self).__init__(error_msg)
