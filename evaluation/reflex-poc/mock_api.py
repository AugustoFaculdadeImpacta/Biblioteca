"""REST local descartável; fixtures fictícias, sem persistência ou saída externa."""
from fastapi import FastAPI, Header, HTTPException, Query
api = FastAPI(title="Biblioteca escolar — API simulada", docs_url="/docs")
BOOKS = [
 {"id":"livro-1","titulo":"A ilha do tesouro","autor":"R. L. Stevenson","categoria":"Aventura","disponiveis":2},
 {"id":"livro-2","titulo":"O pequeno príncipe","autor":"Antoine de Saint-Exupéry","categoria":"Ficção","disponiveis":0},
 {"id":"livro-3","titulo":"Contos da floresta","autor":"Lia Exemplo","categoria":"Contos","disponiveis":1}]
@api.get("/health")
def health(): return {"ok":True,"servico":"simulado-local"}
@api.get("/catalog")
def catalog(mode: str=Query(default="success")):
 if mode=="error": raise HTTPException(503,"Erro fictício solicitado")
 return [] if mode=="empty" else BOOKS
@api.post("/session")
def session(payload:dict):
 role=payload.get("perfil","estudante")
 if role not in {"estudante","bibliotecario"}: raise HTTPException(400,"Perfil inválido")
 return {"token":f"demo-{role}-token","perfil":role,"nome":"Pessoa de demonstração"}
@api.get("/session")
def get_session(x_demo_session:str|None=Header(default=None)):
 if x_demo_session not in {"demo-estudante-token","demo-bibliotecario-token"}: raise HTTPException(401,"Sessão simulada ausente")
 return {"perfil":"bibliotecario" if x_demo_session.endswith("bibliotecario-token") else "estudante"}
@api.post("/loans/request")
def loan_request(x_demo_session:str|None=Header(default=None)):
 if not x_demo_session: raise HTTPException(401,"Entre para solicitar (simulação)")
 return {"status":"solicitado","mensagem":"Solicitação fictícia; sem persistência."}
@api.post("/loans/confirm")
def loan_confirm(x_demo_session:str|None=Header(default=None)):
 require_librarian(x_demo_session); return {"status":"confirmado","mensagem":"Confirmação fictícia."}
@api.get("/reservations")
def reservations(x_demo_session:str|None=Header(default=None)):
 if not x_demo_session: raise HTTPException(401,"Entre para ver a fila")
 return [{"posicao":1,"titulo":"O pequeno príncipe","solicitante":"Estudante fictício"}]
@api.post("/admin/action")
def admin_action(x_demo_session:str|None=Header(default=None)):
 require_librarian(x_demo_session); return {"status":"permitido-na-simulacao"}
def require_librarian(token):
 if not token: raise HTTPException(401,"Sessão ausente")
 if token!="demo-bibliotecario-token": raise HTTPException(403,"Ação administrativa recusada para estudante (simulação)")
