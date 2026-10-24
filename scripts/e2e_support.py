"""Disposable-CI helpers for real browser flows."""
from __future__ import annotations
import asyncio
import json
import sys
import uuid
from sqlalchemy import select
from backend.core.security import get_password_hash
from backend.db.session import AsyncSessionLocal
from backend.models.client import UserModel
from backend.models.enums import RoleEnum
from backend.models.notification import NotificationOutboxModel

async def seed_role(client_id: uuid.UUID, role: RoleEnum, email: str, password: str) -> None:
    async with AsyncSessionLocal() as session:
        user = await session.scalar(select(UserModel).where(UserModel.email == email))
        if user is None:
            session.add(UserModel(client_id=client_id,email=email,full_name=f"Northstar {role.value.title()}",hashed_password=get_password_hash(password),role=role,is_active=True,email_verified=True))
        else:
            user.role=role
            user.hashed_password=get_password_hash(password)
            user.is_active=True
            user.email_verified=True
        await session.commit()

async def notification_statuses(client_id: uuid.UUID) -> list[str]:
    async with AsyncSessionLocal() as session:
        result=await session.execute(select(NotificationOutboxModel.status).where(NotificationOutboxModel.client_id==client_id,NotificationOutboxModel.channel=="email"))
        return list(result.scalars().all())

def main() -> None:
    command,*args=sys.argv[1:]
    if command=="seed-role":
        client_id,role,email,password=args
        asyncio.run(seed_role(uuid.UUID(client_id),RoleEnum(role),email,password))
        print(json.dumps({"email":email,"role":role}))
    elif command=="notification-statuses":
        print(json.dumps(asyncio.run(notification_statuses(uuid.UUID(args[0])))))
    elif command=="dispatch-notifications":
        from backend.workers.tasks import dispatch_pending_notifications
        print(json.dumps(dispatch_pending_notifications.run()))
    else:
        raise SystemExit(f"Unsupported helper command: {command}")

if __name__=="__main__":
    main()
