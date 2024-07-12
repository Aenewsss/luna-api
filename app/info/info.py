import json
from fastapi import Depends, HTTPException
from requests import Session

from app.classes.classes import InfoCreate, InfoResponse
from app.models.models import Info, User

def save_info(info_to_create: InfoCreate, db: Session):

    new_info = Info(**info_to_create.model_dump())
    db.add(new_info)
    db.commit()
    db.refresh(new_info)

    return json.dumps({"message": "Informação salva com sucesso"})

def get_all_info_by_user_phone(user_phone: int, db: Session):

    user = db.query(User).filter(User.phone == user_phone).first()
    
    infos = db.query(Info).filter(Info.user_id == user.id).all()

    if not infos:
        return []

    info_array = [InfoResponse.model_validate(info, from_attributes=True) for info in infos]
    info_str = "\n\n•".join(info.model_dump_json() for info in info_array)
    
    return info_str

def get_all_info(user_id: int, db: Session):
    infos = db.query(Info).filter(Info.user_id == user_id).all()

    if not infos:
        return []

    return [InfoResponse.model_validate(info, from_attributes=True) for info in infos]


def remove_info(id: int, db: Session):
    info = db.query(Info).filter(Info.id == id).first()

    if not info:
        return {"text": "Informação não encontrada"}

    # Delete the Info entry
    db.delete(info)
    db.commit()

    return {"text": "Informação removida com sucesso"}

def update_info(id: int, content: str, db: Session):
    info = db.query(Info).filter(Info.id == id).first()

    if not info:
        return {"text": "Informação não encontrada"}

    print("\ninfo before",info)
    info.content = content
    print("\ninfo after",info)
    db.commit()

    return {"text": "Informação alterada com sucesso"}
