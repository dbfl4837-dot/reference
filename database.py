import os
import json
from collections import Counter
from contextlib import contextmanager
from dotenv import load_dotenv
from sqlalchemy import create_engine, func, or_
from sqlalchemy.orm import Session, sessionmaker
from models import ANALYSIS_JSON_FIELDS, PLAN_JSON_FIELDS, Analysis, Base, Plan, Product, Project, Reference

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/creative_prd_v2.db")
_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

def init_db():
    if DATABASE_URL.startswith("sqlite"):
        os.makedirs("data", exist_ok=True)
    Base.metadata.create_all(bind=engine)

@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def create_project(name: str, memo: str = ""):
    with get_session() as session:
        p = Project(name=name.strip(), memo=memo.strip() or None)
        session.add(p); session.flush(); session.refresh(p); session.expunge(p)
        return p

def list_projects():
    with get_session() as session:
        projects = session.query(Project).order_by(Project.name.asc()).all()
        session.expunge_all(); return projects

def get_project(pid: int):
    with get_session() as session:
        p = session.get(Project, pid)
        if p: session.expunge(p)
        return p

def delete_project(pid: int):
    with get_session() as session:
        p = session.get(Project, pid)
        if p: session.delete(p)

def create_product(project_id: int, name: str, usp_notes: str = "", landing_url: str = "", image_paths: str = ""):
    with get_session() as session:
        p = Product(
            project_id=project_id, 
            name=name.strip(), 
            usp_notes=usp_notes.strip() or None,
            landing_url=landing_url.strip() or None,
            image_paths=image_paths.strip() or None
        )
        session.add(p); session.flush(); session.refresh(p); session.expunge(p)
        return p

def list_products(project_id=None):
    with get_session() as session:
        q = session.query(Product)
        if project_id: q = q.filter(Product.project_id == project_id)
        products = q.order_by(Product.name.asc()).all()
        session.expunge_all(); return products

def get_product(pid: int):
    with get_session() as session:
        p = session.get(Product, pid)
        if p: session.expunge(p)
        return p

def delete_product(pid: int):
    with get_session() as session:
        p = session.get(Product, pid)
        if p: session.delete(p)

def create_reference(**fields):
    vp = fields.pop("video_paths", None)
    tags = fields.pop("tags", None)
    fields.setdefault("is_favorite", False)
    fields.setdefault("is_deleted", False)
    with get_session() as session:
        r = Reference(**fields)
        if vp: r.video_paths = vp if isinstance(vp, str) else json.dumps(vp, ensure_ascii=False)
        if tags: r.tags = tags if isinstance(tags, str) else json.dumps(tags, ensure_ascii=False)
        session.add(r); session.flush(); session.refresh(r); session.expunge(r)
        return r

def save_analysis(rid: int, data: dict, raw_json: str = ""):
    with get_session() as session:
        a = session.query(Analysis).filter_by(reference_id=rid).first()
        if not a: a = Analysis(reference_id=rid); session.add(a)
        for k, v in data.items():
            if k in ANALYSIS_JSON_FIELDS: getattr(a, f"set_{k}")(v)
            elif hasattr(a, k): setattr(a, k, v)
        session.flush(); session.refresh(a); session.expunge(a)
        return a

def save_plan(rid: int, data: dict, raw_json: str = ""):
    with get_session() as session:
        p = session.query(Plan).filter_by(reference_id=rid).first()
        if not p: p = Plan(reference_id=rid); session.add(p)
        for k, v in data.items():
            if k in PLAN_JSON_FIELDS: getattr(p, f"set_{k}")(v)
            elif hasattr(p, k): setattr(p, k, v)
        session.flush(); session.refresh(p); session.expunge(p)
        return p

def search_references(keyword="", project_id=None, product_id=None):
    with get_session() as session:
        q = session.query(Reference).filter(Reference.is_deleted.is_(False))
        if project_id: q = q.filter(Reference.project_id == project_id)
        if product_id: q = q.filter(Reference.product_id == product_id)
        refs = q.order_by(Reference.created_at.desc()).all()
        for r in refs: 
            _ = r.analysis
            _ = r.plan
        session.expunge_all()
        return refs

def delete_reference(rid: int):
    with get_session() as session:
        r = session.get(Reference, rid)
        if r: session.delete(r)

def update_reference_title(rid: int, title: str):
    with get_session() as session:
        r = session.get(Reference, rid)
        if r:
            r.ad_copy_text = title.strip()
            session.flush(); session.refresh(r); session.expunge(r)
        return r

def dashboard_stats():
    with get_session() as session:
        tot = session.query(func.count(Reference.id)).filter(Reference.is_deleted.is_(False)).scalar() or 0
        recent = session.query(Reference).filter(Reference.is_deleted.is_(False)).order_by(Reference.created_at.desc()).limit(5).all()
        bp = session.query(Project.name, func.count(Reference.id)).join(Reference).filter(Reference.is_deleted.is_(False)).group_by(Project.name).all()
        bprod = session.query(Product.name, func.count(Reference.id)).join(Reference).filter(Reference.is_deleted.is_(False)).group_by(Product.name).all()
        session.expunge_all()
        return {"total_references": tot, "recent": recent, "by_project": list(bp), "by_product": list(bprod)}
