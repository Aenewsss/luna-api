import json
from fastapi import Depends
from requests import Session

from app.classes.classes import InfoCreate, InfoResponse
from app.models.models import Info

def save_info(info_to_create: InfoCreate,db: Session):
    
    print('\nline 13',info_to_create,'\n\n')
    
    new_info = Info(**info_to_create.model_dump())
    db.add(new_info)
    db.commit()
    db.refresh(new_info)

    print('new_info',[new_info])
    return json.dumps({"message": "Informação salva com sucesso"})


def get_all_info(user_id: int, db:Session):
    infos = db.query(Info).filter(Info.user_id==user_id).all()
    
    if not infos:
        return []
        
    return [InfoResponse.model_validate(info,from_attributes=True) for info in infos]