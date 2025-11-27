from core.database import Base
from datetime import datetime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, ForeignKey, Boolean, Text, Enum
from auth.models import User
import enum




class RoomRole(enum.Enum):
    OWNER = "owner"    # Создатель, полные права
    ADMIN = "admin"    # Может приглашать/удалять
    MEMBER = "member"  # Просто участник (только чтение/чат)



class RoomMember(Base):
    """Связь пользователя и комнаты с указанием роли"""
    __tablename__ = "room_members"

    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    
    # Роль участника (Владелец, Админ, Участник)
    role: Mapped[RoomRole] = mapped_column(
        Enum(RoomRole), 
        default=RoomRole.MEMBER, 
        nullable=False
    )
    
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Кто пригласил этого пользователя (опционально, но полезно)
    invited_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    # Связи
    room: Mapped["Room"] = relationship("Room", back_populates="members")
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    invited_by: Mapped["User | None"] = relationship("User", foreign_keys=[invited_by_id])

    def __repr__(self):
        return f"RoomMember(room={self.room_id}, user={self.user_id}, role={self.role})"




class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Создатель (техническое поле)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_by: Mapped["User"] = relationship("User", back_populates="created_rooms")

    tasks: Mapped[list["Task"]] = relationship(
        "Task", 
        back_populates="room", 
        cascade="all, delete-orphan" # Удалит задачи, если удалят комнату
    )

    # Список участников (включая владельца)
    members: Mapped[list["RoomMember"]] = relationship(
        "RoomMember", 
        back_populates="room",
        cascade="all, delete-orphan"
    )
    
    # AI анализы комнаты
    ai_analyses: Mapped[list["AIAnalysisHistory"]] = relationship(
        "AIAnalysisHistory",
        back_populates="room",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"Room(id={self.id}, name={self.name})"