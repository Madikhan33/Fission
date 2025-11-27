from core.database import Base
from datetime import datetime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, ForeignKey, Boolean, Text, Enum
import enum


class TaskStatus(enum.Enum):
    """Статусы задачи"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    CANCELLED = "cancelled"


class TaskPriority(enum.Enum):
    """Приоритеты задачи"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskAssignment(Base):
    """Промежуточная таблица для связи задач и ответственных (many-to-many)"""
    __tablename__ = "task_assignments"
    
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    assigned_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    
    # Relationships
    task: Mapped["Task"] = relationship("Task", back_populates="assignments")
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    assigned_by: Mapped["User | None"] = relationship("User", foreign_keys=[assigned_by_id])
    
    def __repr__(self):
        return f"TaskAssignment(task_id={self.task_id}, user_id={self.user_id})"


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rooms.models import Room

class Task(Base):
    """Модель задачи"""
    __tablename__ = "tasks"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    room_id: Mapped[int | None] = mapped_column(ForeignKey("rooms.id", ondelete="CASCADE"), nullable=True)
    
    # --- СВЯЗЬ ---
    room: Mapped["Room"] = relationship("Room", back_populates="tasks")
    
    # Статус и приоритет
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus), 
        default=TaskStatus.TODO, 
        nullable=False
    )
    priority: Mapped[TaskPriority] = mapped_column(
        Enum(TaskPriority), 
        default=TaskPriority.MEDIUM, 
        nullable=False
    )
    
    # Создатель задачи (кто создал)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # Временные метки
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow, 
        nullable=False
    )
    due_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    created_by: Mapped["User"] = relationship("User", foreign_keys=[created_by_id], back_populates="created_tasks")
    assignments: Mapped[list["TaskAssignment"]] = relationship(
        "TaskAssignment", 
        back_populates="task",
        cascade="all, delete-orphan"
    )
    
    # Удобный доступ к ответственным через assignments
    @property
    def assignees(self) -> list["User"]:
        """Получить список всех ответственных за задачу"""
        return [assignment.user for assignment in self.assignments]
    
    def __repr__(self):
        return f"Task(id={self.id}, title={self.title}, status={self.status.value}, priority={self.priority.value})"
