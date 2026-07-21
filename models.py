import datetime
import json
from typing import Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase): pass
def _utcnow(): return datetime.datetime.utcnow()

class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    memo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=_utcnow)
    products: Mapped[list["Product"]] = relationship("Product", back_populates="project", cascade="all, delete-orphan")

class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    usp_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    landing_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_paths: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    project: Mapped["Project"] = relationship("Project", back_populates="products")
    references: Mapped[list["Reference"]] = relationship("Reference", back_populates="product", cascade="all, delete-orphan")

class Reference(Base):
    __tablename__ = "references"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    ad_copy_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    video_paths: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=_utcnow)
    product: Mapped["Product"] = relationship("Product", back_populates="references")
    analysis: Mapped[Optional["Analysis"]] = relationship("Analysis", back_populates="reference", uselist=False, cascade="all, delete-orphan")
    plan: Mapped[Optional["Plan"]] = relationship("Plan", back_populates="reference", uselist=False, cascade="all, delete-orphan")

class Analysis(Base):
    __tablename__ = "analyses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reference_id: Mapped[int] = mapped_column(ForeignKey("references.id", ondelete="CASCADE"), unique=True, nullable=False)
    raw_script: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    step1_full_analysis: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    step1_5_scene_analysis: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # 추가된 부분
    step2_winning_pattern: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    step3_hba_structure: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    step4_behavioral_psychology: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reference: Mapped["Reference"] = relationship("Reference", back_populates="analysis")

    def set_step1_full_analysis(self, v): self.step1_full_analysis = json.dumps(v, ensure_ascii=False)
    def set_step1_5_scene_analysis(self, v): self.step1_5_scene_analysis = json.dumps(v, ensure_ascii=False) # 추가된 부분
    def set_step2_winning_pattern(self, v): self.step2_winning_pattern = json.dumps(v, ensure_ascii=False)
    def set_step3_hba_structure(self, v): self.step3_hba_structure = json.dumps(v, ensure_ascii=False)
    def set_step4_behavioral_psychology(self, v): self.step4_behavioral_psychology = json.dumps(v, ensure_ascii=False)

ANALYSIS_JSON_FIELDS = {"step1_full_analysis", "step1_5_scene_analysis", "step2_winning_pattern", "step3_hba_structure", "step4_behavioral_psychology"}

class Plan(Base):
    __tablename__ = "plans"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reference_id: Mapped[int] = mapped_column(ForeignKey("references.id", ondelete="CASCADE"), unique=True, nullable=False)
    step5_brand_direction: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    step6_ad_formulas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    step7_new_scripts: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    step8_cheat_keys: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    step9_final_priority: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reference: Mapped["Reference"] = relationship("Reference", back_populates="plan")

    def set_step5_brand_direction(self, v): self.step5_brand_direction = json.dumps(v, ensure_ascii=False)
    def set_step6_ad_formulas(self, v): self.step6_ad_formulas = json.dumps(v, ensure_ascii=False)
    def set_step7_new_scripts(self, v): self.step7_new_scripts = json.dumps(v, ensure_ascii=False)
    def set_step8_cheat_keys(self, v): self.step8_cheat_keys = json.dumps(v, ensure_ascii=False)
    def set_step9_final_priority(self, v): self.step9_final_priority = json.dumps(v, ensure_ascii=False)

PLAN_JSON_FIELDS = {"step5_brand_direction", "step6_ad_formulas", "step7_new_scripts", "step8_cheat_keys", "step9_final_priority"}