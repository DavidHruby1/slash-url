from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Index, ForeignKey, DateTime, String, func
from datetime import datetime, timezone


class Base(DeclarativeBase):
    pass


class Link(Base):
    __tablename__ = "links"

    # columns
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False
    )
    original_url: Mapped[str] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False
    )
    clicks: Mapped[int] = mapped_column(
        server_default="0",
        default=0,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        server_default="true",
        default=True,
        nullable=False
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    max_clicks: Mapped[int | None]

    # indexes
    __table_args__ = (
        Index("ix_links_created_at", "created_at"),
        Index("ix_links_is_active", "is_active"),
    )

    # relationships
    related_clicks: Mapped[list["Click"]] = relationship(
        back_populates="related_link",
        cascade="all"
    ) 


class Click(Base):
    __tablename__ = "clicks"

    # columns
    id: Mapped[int] = mapped_column(primary_key=True)
    clicked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    user_agent: Mapped[str | None]
    referer: Mapped[str | None]
    language: Mapped[str | None]
    device: Mapped[str | None]
    browser: Mapped[str | None]
    os: Mapped[str | None]

    # indexes
    __table_args__ = (
        Index("ix_clicks_link_id", "link_id"),
        Index("ix_clicks_link_id_clicked_at", "link_id", "clicked_at")
    )

    # relationships
    link_id: Mapped[int] = mapped_column(
        ForeignKey("links.id", ondelete="CASCADE")
    )
    related_link: Mapped["Link"] = relationship(back_populates="related_clicks")
