from core.database import Base
from datetime import datetime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, ForeignKey, Boolean, Text


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_lead: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    created_tasks: Mapped[list["Task"]] = relationship(
        "Task", 
        foreign_keys="Task.created_by_id",
        back_populates="created_by",
        cascade="all, delete-orphan"
    )

    resume_analysis: Mapped["ResumeAnalysis"] = relationship(
        "ResumeAnalysis",
        back_populates="user",
        uselist=False  # один пользователь -> одно резюме
    )

    # Созданные комнаты
    created_rooms: Mapped[list["Room"]] = relationship(
        "Room",
        foreign_keys="Room.created_by_id",
        back_populates="created_by"
    )

    
    # Это нужно, чтобы проверить права, роль или получить список "Мои комнаты"
    room_memberships: Mapped[list["RoomMember"]] = relationship(
        "RoomMember", 
        foreign_keys="RoomMember.user_id",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # Notifications
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    

    def __repr__(self):
        return f"User(id={self.id}, username={self.username}, email={self.email}, is_lead={self.is_lead})"
