from typing import Optional
import pymysql
from pymysql.cursors import DictCursor
from contextlib import contextmanager

class DatabaseConnectionPool:
    _instance: Optional['DatabaseConnectionPool'] = None

    def __init__(self, host: str, port: int, user: str, password: str, database: str, pool_size: int = 5):
        """Initialize the connection pool."""
        if DatabaseConnectionPool._instance is not None:
            raise RuntimeError("Use get_instance() to access DatabaseConnectionPool")
        
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.pool_size = pool_size
        self._connections = []

    @classmethod
    def get_instance(cls, host: str = None, port: int = None, user: str = None,
                    password: str = None, database: str = None, pool_size: int = 5) -> 'DatabaseConnectionPool':
        """Get or create the singleton instance of DatabaseConnectionPool."""
        if cls._instance is None:
            if not all([host, port, user, password, database]):
                raise ValueError("All connection parameters must be provided when creating the pool")
            cls._instance = DatabaseConnectionPool(host, port, user, password, database, pool_size)
        return cls._instance

    def _create_connection(self):
        """Create a new database connection."""
        return pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            cursorclass=DictCursor,
            autocommit=False
        )

    @contextmanager
    def get_connection(self):
        """Get a connection from the pool."""
        connection = None
        try:
            # Try to get an existing connection
            if self._connections:
                connection = self._connections.pop()
                try:
                    # Test if connection is still alive
                    connection.ping(reconnect=True)
                except:
                    # Connection is dead, create new one
                    connection = self._create_connection()
            else:
                # Create new connection
                connection = self._create_connection()

            yield connection

            # Return connection to pool if it's still usable
            try:
                if not connection.open:
                    connection = self._create_connection()
                self._connections.append(connection)
            except:
                # If connection is unusable, create new one for pool
                self._connections.append(self._create_connection())

        except Exception as e:
            # If any error occurs, ensure connection is closed
            if connection:
                try:
                    connection.close()
                except:
                    pass
            raise e

    def close_all(self):
        """Close all connections in the pool."""
        for conn in self._connections:
            try:
                conn.close()
            except:
                pass
        self._connections.clear()

    def __del__(self):
        """Ensure all connections are closed when object is destroyed."""
        self.close_all() 