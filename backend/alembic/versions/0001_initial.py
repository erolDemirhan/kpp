"""initial schema"""
from alembic import op
from app import models  # noqa: F401
from app.database import Base

revision = "0001"
down_revision = branch_labels = depends_on = None
def upgrade(): Base.metadata.create_all(bind=op.get_bind())
def downgrade(): Base.metadata.drop_all(bind=op.get_bind())
