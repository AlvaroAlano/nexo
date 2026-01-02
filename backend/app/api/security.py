from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.tables import User

def get_current_user(db: Session = Depends(get_db)) -> User:
    """
    Dependência que recupera o usuário logado.
    
    NOTA PARA SAAS:
    Atualmente, retorna sempre o 'usuario@exemplo.com' para facilitar o desenvolvimento
    e testes sem precisar fazer login via Token JWT a todo momento.
    
    No futuro, substituiremos a lógica abaixo pela decodificação do Token (Bearer Token)
    para identificar quem é o usuário real fazendo a requisição.
    """
    
    # Busca o usuário padrão criado no main.py
    user = db.query(User).filter(User.email == "usuario@exemplo.com").first()
    
    if not user:
        # Se por algum motivo o init_db não rodou ou o usuário sumiu
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não foi possível autenticar o usuário padrão de desenvolvimento.",
        )
        
    return user