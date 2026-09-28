from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


# ============================================================
# PART MASTER
# ============================================================

class Part(Base):
    __tablename__ = "parts"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    fcl_part_code: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    canonical_description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    normalized_description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    current_price: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 2),
        nullable=True,
    )

    unit: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    aliases = relationship(
        "PartAlias",
        back_populates="part",
        cascade="all, delete-orphan",
    )


class PartAlias(Base):
    __tablename__ = "part_aliases"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    part_id: Mapped[int] = mapped_column(
        ForeignKey("parts.id"),
        nullable=False,
        index=True,
    )

    alias_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    normalized_alias: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
    )

    source: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    part = relationship(
        "Part",
        back_populates="aliases",
    )

    __table_args__ = (
        UniqueConstraint(
            "part_id",
            "normalized_alias",
            name="uq_part_alias_normalized",
        ),
    )


# ============================================================
# IMPORT / STAGING
# ============================================================

class ImportBatch(Base):
    __tablename__ = "import_batches"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    # PART_MASTER / CUSTOMER_RFQ / HISTORICAL_RFQ
    import_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    stored_filename: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # UPLOADED / MAPPED / VALIDATED / STAGED / REVIEWED /
    # CONFIRMED / REJECTED
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="UPLOADED",
        index=True,
    )

    selected_sheet: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    header_row: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    column_mapping: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    total_rows: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    valid_rows: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    warning_rows: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    error_rows: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    created_by_ref: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    confirmed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    staged_rows = relationship(
        "StagedImportRow",
        back_populates="batch",
        cascade="all, delete-orphan",
    )


class StagedImportRow(Base):
    __tablename__ = "staged_import_rows"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    batch_id: Mapped[int] = mapped_column(
        ForeignKey("import_batches.id"),
        nullable=False,
        index=True,
    )

    row_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    raw_data: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    normalized_data: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # VALID / WARNING / ERROR
    validation_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    validation_messages: Mapped[list | dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    original_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    normalized_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    suggested_part_id: Mapped[int | None] = mapped_column(
        ForeignKey("parts.id"),
        nullable=True,
    )

    # EXACT / ALIAS / FUZZY / MANUAL / NONE
    match_type: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    match_score: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )

    confirmed_part_id: Mapped[int | None] = mapped_column(
        ForeignKey("parts.id"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    batch = relationship(
        "ImportBatch",
        back_populates="staged_rows",
    )

    __table_args__ = (
        UniqueConstraint(
            "batch_id",
            "row_number",
            name="uq_staged_batch_row",
        ),
    )


# ============================================================
# RFQ
# ============================================================

class RFQ(Base):
    __tablename__ = "rfqs"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    fcl_enquiry_no: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    received_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    customer_id_ref: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    customer_name_snapshot: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    industry_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    request_from: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    sales_person_ref: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    assigned_engineer_ref: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    rd_review_ref: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # Stored as string until Fluid Controls confirms final workflow.
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    remarks: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    requirement_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    ga_drawing_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    bought_out_request_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    bought_out_quotation_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    received_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    completion_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    # MANUAL / CUSTOMER_EXCEL / HISTORICAL_IMPORT
    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    import_batch_id: Mapped[int | None] = mapped_column(
        ForeignKey("import_batches.id"),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    items = relationship(
        "RFQItem",
        back_populates="rfq",
        cascade="all, delete-orphan",
    )

    status_history = relationship(
        "RFQStatusHistory",
        back_populates="rfq",
        cascade="all, delete-orphan",
    )

    quotations = relationship(
        "Quotation",
        back_populates="rfq",
        cascade="all, delete-orphan",
    )


class RFQItem(Base):
    __tablename__ = "rfq_items"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    rfq_id: Mapped[int] = mapped_column(
        ForeignKey("rfqs.id"),
        nullable=False,
        index=True,
    )

    line_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    original_item_description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    normalized_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    matched_part_id: Mapped[int | None] = mapped_column(
        ForeignKey("parts.id"),
        nullable=True,
        index=True,
    )

    customer_part_code: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # Nullable intentionally until quantity rules are confirmed.
    quantity: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 3),
        nullable=True,
    )

    unit: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    # Historical price snapshot.
    quoted_unit_price: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 2),
        nullable=True,
    )

    line_total: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 2),
        nullable=True,
    )

    match_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="UNMATCHED",
    )

    match_score: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )

    manual_override: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    remarks: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    rfq = relationship(
        "RFQ",
        back_populates="items",
    )

    __table_args__ = (
        UniqueConstraint(
            "rfq_id",
            "line_number",
            name="uq_rfq_line_number",
        ),
    )


class RFQStatusHistory(Base):
    __tablename__ = "rfq_status_history"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    rfq_id: Mapped[int] = mapped_column(
        ForeignKey("rfqs.id"),
        nullable=False,
        index=True,
    )

    previous_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    new_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    changed_by_ref: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    changed_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        index=True,
    )

    rfq = relationship(
        "RFQ",
        back_populates="status_history",
    )


# ============================================================
# QUOTATIONS
# ============================================================

class Quotation(Base):
    __tablename__ = "quotations"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    rfq_id: Mapped[int] = mapped_column(
        ForeignKey("rfqs.id"),
        nullable=False,
        index=True,
    )

    revision_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="DRAFT",
        index=True,
    )

    subtotal: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 2),
        nullable=True,
    )

    # Reserved for future confirmed commercial adjustments.
    adjustment_data: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    total: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 2),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    confirmed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    rfq = relationship(
        "RFQ",
        back_populates="quotations",
    )

    items = relationship(
        "QuotationItem",
        back_populates="quotation",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            "rfq_id",
            "revision_number",
            name="uq_quotation_rfq_revision",
        ),
    )


class QuotationItem(Base):
    __tablename__ = "quotation_items"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    quotation_id: Mapped[int] = mapped_column(
        ForeignKey("quotations.id"),
        nullable=False,
        index=True,
    )

    rfq_item_id: Mapped[int] = mapped_column(
        ForeignKey("rfq_items.id"),
        nullable=False,
        index=True,
    )

    part_id: Mapped[int | None] = mapped_column(
        ForeignKey("parts.id"),
        nullable=True,
    )

    description_snapshot: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    fcl_part_code_snapshot: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    quantity_snapshot: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 3),
        nullable=True,
    )

    unit_price_snapshot: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 2),
        nullable=True,
    )

    line_total: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 2),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    quotation = relationship(
        "Quotation",
        back_populates="items",
    )


Index(
    "ix_parts_normalized_description_prefix",
    Part.normalized_description,
    mysql_length=255,
)
