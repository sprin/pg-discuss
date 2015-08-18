"""
The SQLAlchemy Expression Language is preferred for CRUD operations, so
shorter aliases are created for the table objects are created here.
"""
from . import models


thread = models.Thread.__table__
comment = models.Comment.__table__
