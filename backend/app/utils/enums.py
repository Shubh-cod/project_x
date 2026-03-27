"""All Enum definitions for NovaCRM."""
import enum


class UserRole(str, enum.Enum):
    admin = "admin"
    manager = "manager"
    agent = "agent"


class LeadStatus(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    LOST = "lost"


class LeadPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class LeadSource(str, enum.Enum):
    WEB = "web"
    REFERRAL = "referral"
    COLD_CALL = "cold-call"
    OTHER = "other"


class DealStage(str, enum.Enum):
    PROSPECT = "prospect"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"


class TaskStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ActivityAction(str, enum.Enum):
    CREATED = "created"
    UPDATED = "updated"
    STATUS_CHANGED = "status_changed"
    ASSIGNED = "assigned"
    NOTE_ADDED = "note_added"
    CONVERTED = "converted"


class EntityType(str, enum.Enum):
    CONTACT = "contact"
    LEAD = "lead"
    DEAL = "deal"
