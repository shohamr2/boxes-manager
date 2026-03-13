import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, func, Identity
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, joinedload

Base = declarative_base()


class Box(Base):
    __tablename__ = "boxes"
    id = Column(Integer, Identity(), primary_key=True)
    name = Column(String, nullable=False)
    photo = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    items = relationship("Item", back_populates="box", cascade="all, delete-orphan")


class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, Identity(), primary_key=True)
    name = Column(String, nullable=False)
    photo = Column(String)
    quantity = Column(Integer, default=1)
    box_id = Column(Integer, ForeignKey("boxes.id"), nullable=False)
    box = relationship("Box", back_populates="items")

DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine, expire_on_commit=False)

def create_box(box_name, photo=None):
    with Session() as session:
        box = Box(name=box_name, photo=photo or "none")
        session.add(box)
        session.commit()
        return box


def add_item(item_name, box_id, photo=None, quantity=1):
    with Session() as session:
        item = Item(
            name=item_name,
            photo=photo or "none",
            box_id=box_id,
            quantity=quantity,
        )
        session.add(item)
        session.commit()
        return item


def get_boxes():
    with Session() as session:
        return session.query(Box).order_by(Box.id.desc()).all()


def get_boxes_with_counts():
    with Session() as session:
        rows = (
            session.query(Box, func.count(Item.id).label("item_count"), func.coalesce(func.sum(Item.quantity), 0).label("total_quantity"))
            .outerjoin(Item, Box.id == Item.box_id)
            .group_by(Box.id)
            .order_by(Box.id.desc())
            .all()
        )
        return [
            {"box": box, "count": int(item_count or 0), "total_quantity": int(total_quantity or 0)}
            for box, item_count, total_quantity in rows
        ]


def get_box(box_id):
    with Session() as session:
        return session.get(Box, box_id)


def get_items_in_box(box_id):
    with Session() as session:
        return (
            session.query(Item)
            .filter_by(box_id=box_id)
            .order_by(Item.name.asc(), Item.id.asc())
            .all()
        )


def get_item(item_id):
    with Session() as session:
        return session.query(Item).options(joinedload(Item.box)).filter(Item.id == item_id).first()


def search_all(term, limit=20):
    clean_term = (term or "").strip()
    if not clean_term:
        return {"items": [], "boxes": []}

    with Session() as session:
        item_results = (
            session.query(Item)
            .options(joinedload(Item.box))
            .filter(Item.name.ilike(f"%{clean_term}%"))
            .order_by(Item.name.asc())
            .limit(limit)
            .all()
        )
        box_results = (
            session.query(Box)
            .filter(Box.name.ilike(f"%{clean_term}%"))
            .order_by(Box.name.asc())
            .limit(limit)
            .all()
        )
        return {"items": item_results, "boxes": box_results}


def get_box_of_item(item_id):
    with Session() as session:
        item = session.query(Item).options(joinedload(Item.box)).filter(Item.id == item_id).first()
        return item.box if item else None


def increase_quantity(item_id):
    with Session() as session:
        item = session.get(Item, item_id)
        if not item:
            return None
        item.quantity += 1
        session.commit()
        return item


def decrease_quantity(item_id):
    with Session() as session:
        item = session.get(Item, item_id)
        if not item:
            return None
        if item.quantity > 1:
            item.quantity -= 1
        session.commit()
        return item


def update_item_quantity(item_id, quantity):
    with Session() as session:
        item = session.get(Item, item_id)
        if not item:
            return None
        item.quantity = quantity
        session.commit()
        return item


def update_box_data(box_id, name, photo=None):
    with Session() as session:
        box = session.get(Box, box_id)
        if not box:
            return None
        box.name = name
        if photo is not None:
            box.photo = photo
        session.commit()
        return box


def update_item_data(item_id, name, quantity=None, photo=None, box_id=None):
    with Session() as session:
        item = session.get(Item, item_id)
        if not item:
            return None
        item.name = name
        if quantity is not None:
            item.quantity = quantity
        if photo is not None:
            item.photo = photo
        if box_id is not None:
            item.box_id = box_id
        session.commit()
        return item


def move_item_to_box(item_id, new_box_id):
    with Session() as session:
        item = session.get(Item, item_id)
        target_box = session.get(Box, new_box_id)
        if not item or not target_box:
            return None
        item.box_id = new_box_id
        session.commit()
        return item


def delete_item_by_id(item_id):
    with Session() as session:
        item = session.get(Item, item_id)
        if not item:
            return None
        photo = item.photo
        box_id = item.box_id
        session.delete(item)
        session.commit()
        return {"photo": photo, "box_id": box_id}


def delete_box_by_id(box_id):
    with Session() as session:
        box = session.query(Box).options(joinedload(Box.items)).filter(Box.id == box_id).first()
        if not box:
            return None
        photos = [box.photo] + [item.photo for item in box.items]
        session.delete(box)
        session.commit()
        return {"photos": photos}


def get_statistics():
    with Session() as session:
        total_boxes = session.query(func.count(Box.id)).scalar() or 0
        total_item_types = session.query(func.count(Item.id)).scalar() or 0
        total_quantity = session.query(func.coalesce(func.sum(Item.quantity), 0)).scalar() or 0
        return {
            "total_boxes": int(total_boxes),
            "total_item_types": int(total_item_types),
            "total_quantity": int(total_quantity),
        }
