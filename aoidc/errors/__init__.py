class GenericError(Exception):
    pass


class GenericAuthError(GenericError):
    pass


class GenericValidationError(ValueError, GenericError):
    pass


class GenericOIDCError(GenericError): ...
