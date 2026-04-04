import csv
import io
import re
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy import select, func, and_, or_, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.contact import Contact
from app.utils.logging import logger
from app.models.note import Note
from app.models.tag import Tag, contact_tags
from app.utils.pagination import paginate
from app.utils.exceptions import NotFoundError
from app.services.activity_service import log as activity_log
from app.services.search_service import invalidate_search_cache
from app.services.dashboard_service import invalidate_dashboard_cache
from app.schemas.contact import ContactCreate, ContactUpdate, ContactListFilters


async def create(
    session: AsyncSession,
    data: ContactCreate,
    user_id: Optional[UUID] = None,
) -> Contact:
    contact = Contact(
        name=data.name,
        email=data.email,
        phone=data.phone,
        company=data.company,
        address=data.address,
        source=data.source,
        notes=data.notes,
        assigned_to=data.assigned_to,
        owner_id=user_id,
    )
    session.add(contact)
    await session.flush()
    logger.info("Created contact: %s (ID: %s)", contact.name, contact.id)
    # ── Auto-create a Note record if notes were provided ──
    if data.notes and data.notes.strip():
        note = Note(
            entity_type="contact",
            entity_id=contact.id,
            content=data.notes.strip(),
            owner_id=user_id,
            created_by=user_id,
        )
        session.add(note)

    if data.tags:
        await _set_contact_tags(session, contact.id, data.tags)
    await activity_log(session, "contact", contact.id, "created", user_id, {"entity_name": contact.name})
    await invalidate_search_cache()
    await invalidate_dashboard_cache(contact.assigned_to)
    await session.refresh(contact)
    return contact


async def get_by_id(session: AsyncSession, contact_id: UUID, user_id: Optional[UUID] = None) -> Contact | None:
    q = (
        select(Contact)
        .where(and_(Contact.id == contact_id, Contact.is_deleted == False))
        .options(selectinload(Contact.tags))
    )
    if user_id is not None:
        q = q.where(Contact.owner_id == user_id)
    result = await session.execute(q)
    return result.scalar_one_or_none()


async def list_contacts(
    session: AsyncSession,
    filters: ContactListFilters,
    user_id: Optional[UUID] = None,
) -> tuple[list[Contact], int]:
    q = (
        select(Contact)
        .where(Contact.is_deleted == False)
        .options(selectinload(Contact.tags))
    )
    # ── Data isolation: always filter by owner ──
    if user_id is not None:
        q = q.where(Contact.owner_id == user_id)
    if filters.name:
        q = q.where(Contact.name.ilike(f"%{filters.name}%"))
    if filters.email:
        q = q.where(Contact.email.ilike(f"%{filters.email}%"))
    if filters.assigned_to:
        q = q.where(Contact.assigned_to == filters.assigned_to)
    if filters.date_from:
        q = q.where(Contact.created_at >= filters.date_from)
    if filters.date_to:
        q = q.where(Contact.created_at <= filters.date_to)
    if filters.tag:
        sub = select(contact_tags.c.contact_id).select_from(contact_tags).join(Tag, contact_tags.c.tag_id == Tag.id).where(Tag.name == filters.tag)
        q = q.where(Contact.id.in_(sub))
    q = q.order_by(Contact.created_at.desc())
    return await paginate(session, q, filters.page, filters.page_size)


async def update(
    session: AsyncSession,
    contact_id: UUID,
    data: ContactUpdate,
    user_id: Optional[UUID] = None,
) -> Contact | None:
    contact = await get_by_id(session, contact_id, user_id=user_id)
    if not contact:
        return None
    if data.name is not None:
        contact.name = data.name
    if data.email is not None:
        contact.email = data.email
    if data.phone is not None:
        contact.phone = data.phone
    if data.company is not None:
        contact.company = data.company
    if data.address is not None:
        contact.address = data.address
    if data.source is not None:
        contact.source = data.source
    if data.notes is not None:
        contact.notes = data.notes
    if data.assigned_to is not None:
        contact.assigned_to = data.assigned_to
    if data.tags is not None:
        await _set_contact_tags(session, contact.id, data.tags)
    await activity_log(session, "contact", contact.id, "updated", user_id, {"entity_name": contact.name})
    await invalidate_search_cache()
    await invalidate_dashboard_cache(contact.assigned_to)
    await session.flush()
    await session.refresh(contact)
    return contact


async def soft_delete(
    session: AsyncSession,
    contact_id: UUID,
    user_id: Optional[UUID] = None,
    delete_associated: bool = False,
) -> bool:
    contact = await get_by_id(session, contact_id, user_id=user_id)
    if not contact:
        return False
    contact.is_deleted = True

    if delete_associated:
        from sqlalchemy import update
        from app.models.lead import Lead
        from app.models.deal import Deal
        from app.models.task import Task

        # Cascade to Leads
        await session.execute(
            update(Lead)
            .where(and_(Lead.contact_id == contact_id, Lead.is_deleted == False))
            .values(is_deleted=True)
        )
        # Cascade to Deals
        await session.execute(
            update(Deal)
            .where(and_(Deal.contact_id == contact_id, Deal.is_deleted == False))
            .values(is_deleted=True)
        )
        # Cascade to Tasks (polymorphic link)
        await session.execute(
            update(Task)
            .where(and_(
                Task.linked_to_id == contact_id,
                Task.linked_to_type == "contact",
                Task.is_deleted == False
            ))
            .values(is_deleted=True)
        )

    await invalidate_search_cache()
    await invalidate_dashboard_cache(contact.assigned_to)
    await session.flush()
    return True


async def import_contacts(
    session: AsyncSession,
    file_content: bytes,
    user_id: UUID,
) -> Dict[str, Any]:
    """Import contacts from CSV with field mapping and validation."""
    logger.info("Starting CSV import for user %s", user_id)
    
    # Handle UTF-8 with BOM automatically
    try:
        content = file_content.decode("utf-8-sig")
    except UnicodeDecodeError:
        # Fallback for other potential encodings like latin-1
        content = file_content.decode("latin-1")
    
    # Detect dialect (delimiter, etc.)
    try:
        dialect = csv.Sniffer().sniff(content[:2048])
    except Exception as e:
        logger.debug("CSV Sniffer failed: %s. Falling back to default comma delimiter.", e)
        dialect = "excel"  # Default comma-separated dialect
    
    reader = csv.DictReader(io.StringIO(content), dialect=dialect)
    
    # Normalize headers for better matching
    original_headers = reader.fieldnames or []
    headers = {h: h.strip().lower().replace(" ", "_").replace("-", "_") for h in original_headers}
    logger.info("Detected headers: %s (Detected Delimiter: '%s')", original_headers, getattr(dialect, 'delimiter', ','))
    
    # Expected fields mapping
    FIELD_MAP = {
        "name": ["name", "full_name", "contact_name", "first_name"],
        "email": ["email", "e_mail", "email_address"],
        "phone": ["phone", "phone_number", "mobile", "tel"],
        "company": ["company", "company_name", "organization", "org"],
        "address": ["address", "location", "street"],
        "notes": ["notes", "description", "info", "extra", "comment", "about"],
        "tags": ["tags", "labels", "categories", "tag"]
    }
    
    def resolve_field(row: Dict[str, str], target: str) -> Optional[str]:
        for alias in FIELD_MAP.get(target, []):
            for h, normalized in headers.items():
                if normalized == alias:
                    val = row.get(h)
                    return val.strip() if val else None
        return None

    results = {
        "total_rows": 0,
        "success_count": 0,
        "failed_count": 0,
        "errors": []
    }
    
    row_num = 1  # 1-indexed (after header)
    for row in reader:
        row_num += 1
        results["total_rows"] += 1
        
        try:
            name = resolve_field(row, "name")
            email = resolve_field(row, "email")
            phone = resolve_field(row, "phone")
            company = resolve_field(row, "company")
            address = resolve_field(row, "address")
            notes = resolve_field(row, "notes")
            tag_str = resolve_field(row, "tags")
            
            if not name:
                logger.warning("Row %d: Missing required field 'name'", row_num)
                results["failed_count"] += 1
                results["errors"].append({"row": row_num, "error": "Missing required field: 'name'"})
                continue
            
            # Email format validation
            if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                logger.warning("Row %d: Invalid email format '%s'", row_num, email)
                results["failed_count"] += 1
                results["errors"].append({"row": row_num, "error": f"Invalid email format: {email}"})
                continue
                
            # Duplicate check by email for this user
            if email:
                exists_query = select(Contact).where(
                    and_(Contact.email == email, Contact.owner_id == user_id, Contact.is_deleted == False)
                )
                if (await session.execute(exists_query)).scalar_one_or_none():
                    logger.info("Row %d: Duplicate contact found for email %s", row_num, email)
                    results["failed_count"] += 1
                    results["errors"].append({"row": row_num, "error": f"Duplicate contact (email exists): {email}"})
                    continue

            # Create contact
            contact = Contact(
                name=name,
                email=email,
                phone=phone,
                company=company,
                address=address,
                notes=notes,
                owner_id=user_id,
                assigned_to=user_id,  # Default to self
            )
            session.add(contact)
            await session.flush()
            
            # Handle tags
            if tag_str:
                tag_names = [t.strip() for t in tag_str.split(",") if t.strip()]
                # Ensure tags exist or create them (global)
                for t_name in tag_names:
                    r = await session.execute(select(Tag).where(Tag.name == t_name))
                    tag = r.scalar_one_or_none()
                    if not tag:
                        tag = Tag(name=t_name)
                        session.add(tag)
                        await session.flush()
                    
                    # Attach tag
                    await session.execute(contact_tags.insert().values(contact_id=contact.id, tag_id=tag.id))

            # Auto-create Note if notes provided
            if notes:
                note = Note(
                    entity_type="contact",
                    entity_id=contact.id,
                    content=notes,
                    owner_id=user_id,
                    created_by=user_id,
                )
                session.add(note)
            
            await activity_log(session, "contact", contact.id, "created (imported)", user_id, {"entity_name": contact.name})
            logger.debug("Row %d: Successfully imported contact %s", row_num, contact.name)
            results["success_count"] += 1
            
        except Exception as e:
            logger.error("Row %d: Unexpected error during import: %s", row_num, str(e), exc_info=True)
            results["failed_count"] += 1
            results["errors"].append({"row": row_num, "error": str(e)})

    logger.info(
        "Import completed for user %s: %d total, %d success, %d failed",
        user_id, results["total_rows"], results["success_count"], results["failed_count"]
    )
    await invalidate_search_cache()
    await invalidate_dashboard_cache(user_id)
    await session.commit()  # Final commit for all rows
    return results


async def _set_contact_tags(session: AsyncSession, contact_id: UUID, tag_names: list[str]) -> None:
    await session.execute(contact_tags.delete().where(contact_tags.c.contact_id == contact_id))
    for name in tag_names:
        r = await session.execute(select(Tag).where(Tag.name == name.strip()))
        tag = r.scalar_one_or_none()
        if not tag:
            # Create if missing
            tag = Tag(name=name.strip())
            session.add(tag)
            await session.flush()
        
        await session.execute(contact_tags.insert().values(contact_id=contact_id, tag_id=tag.id))
    await session.flush()
