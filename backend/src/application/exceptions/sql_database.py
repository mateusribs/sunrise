class SQLDatabaseError(Exception):
    """Base class for all database-related exceptions."""

    pass


class EntityAlreadyExistsError(SQLDatabaseError):
    """Exception raised for integrity constraint violations."""

    pass


class EntityNotFoundError(SQLDatabaseError):
    """Exception raised when an entity is not found."""

    pass


class IntegrityConstraintViolationError(SQLDatabaseError):
    """Exception raised for integrity constraint violations."""

    pass
