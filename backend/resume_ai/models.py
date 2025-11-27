from core.database import Base
from datetime import datetime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, ForeignKey, Text

class ResumeAnalysis(Base):
    __tablename__ = "resume_analysis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Основная информация (для идентификации)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(50))
    location: Mapped[str | None] = mapped_column(String(255))
    
    # Ключевая профессиональная информация (для AI-агента)
    current_position: Mapped[str | None] = mapped_column(String(255))  # текущая должность
    years_of_experience: Mapped[int | None] = mapped_column(Integer)  # общий опыт в годах
    career_level: Mapped[str | None] = mapped_column(String(50))  # junior/middle/senior/lead
    
    # Самое важное для векторного поиска
    professional_summary: Mapped[str | None] = mapped_column(Text)  # краткое описание профиля (2-3 предложения)
    core_skills: Mapped[str | None] = mapped_column(Text)  # JSON: топ 10-15 ключевых навыков
    work_experience_summary: Mapped[str | None] = mapped_column(Text)  # сжатый опыт работы (компании + роли)
    project_experience_summary: Mapped[str | None] = mapped_column(Text)  # сжатый самари именно в каких проектах работал
    
    # Дополнительно (опционально)
    education_summary: Mapped[str | None] = mapped_column(String(500))  # степень + университет
    languages: Mapped[str | None] = mapped_column(String(255))  # JSON: ["English: fluent", "Russian: native"]
    
    # Метаданные
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="resume_analysis")

    def __repr__(self):
        return f"ResumeAnalysis(id={self.id}, name='{self.full_name}', position='{self.current_position}')"
