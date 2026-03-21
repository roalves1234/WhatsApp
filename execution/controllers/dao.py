class BaseDAO:
    """
    Base Data Access Object.
    All persistence is done in the DAO, which is accessed by the Controllers.
    For SQL, use direct code, without ORM.
    """
    def __init__(self, connection_string: str = None):
        self.connection_string = connection_string

    def execute_query(self, query: str, params: tuple = ()):
        # Placeholder for direct SQL execution
        pass
