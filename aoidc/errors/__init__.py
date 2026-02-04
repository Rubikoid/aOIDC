class GenericError(Exception):
    pass


class GenericAuthError(GenericError):
    pass


class GenericValidationError(ValueError, GenericError):
    pass


class GenericOAuthError(GenericError): ...


class GenericOIDCError(GenericError): ...
