class Error(Exception):
    pass

class AuthError(Error):
    pass

class APIError(Error):
    pass

class RepoNotFoundError(Error):
    pass

class UninitializedBuildError(Error):
    pass
