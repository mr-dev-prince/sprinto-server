from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from datetime import datetime, timezone

async def create_user_from_clerk(db, data: dict) -> User:
    clerk_user_id = data["id"]

    primary_email_id = data.get("primary_email_address_id")
    email = None
    for e in data.get("email_addresses", []):
        if e["id"] == primary_email_id:
            email = e["email_address"]
            break

    if not email:
        raise ValueError("Primary email not found")

    first = data.get("first_name") or ""
    last = data.get("last_name") or ""
    name = f"{first} {last}".strip() or "Splito User"
    avatar_url = data.get("image_url")

    result = await db.execute(
        select(User).where(User.clerk_user_id == clerk_user_id)
    )
    user = result.scalar_one_or_none()

    if user:
        if not user.is_active or user.deleted_at:
            user.is_active = True
            user.deleted_at = None

        user.email = email
        user.name = name
        user.avatar_url = avatar_url

        await db.commit()
        await db.refresh(user)
        return user

    result = await db.execute(
        select(User).where(User.email == email)
    )
    user = result.scalar_one_or_none()

    if user:
        user.clerk_user_id = clerk_user_id
        user.is_active = True
        user.deleted_at = None
        user.name = name
        user.avatar_url = avatar_url

        await db.commit()
        await db.refresh(user)
        return user

    user = User(
        clerk_user_id=clerk_user_id,
        email=email,
        name=name,
        avatar_url=avatar_url,
        is_active=True,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user

async def update_user_from_clerk(
    db: AsyncSession,
    data: dict
):
    clerk_user_id = data["id"]

    result = await db.execute(
        select(User).where(User.clerk_user_id == clerk_user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        return None  # user not created yet

    email_addresses = data.get("email_addresses", [])
    if email_addresses:
        user.email = email_addresses[0]["email_address"]

    first_name = data.get("first_name") or ""
    last_name = data.get("last_name") or ""
    user.name = f"{first_name} {last_name}".strip() or user.name

    user.avatar_url = data.get("image_url")

    await db.commit()
    await db.refresh(user)

    return user

async def deactivate_user_from_clerk(
    db: AsyncSession,
    data: dict,
):
    clerk_user_id = data.get("id")
    if not clerk_user_id:
        return None

    result = await db.execute(
        select(User).where(User.clerk_user_id == clerk_user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        # webhook may arrive for a user you never stored
        return None

    # Idempotent: safe to run multiple times
    user.is_active = False
    user.deleted_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(user)

    return user