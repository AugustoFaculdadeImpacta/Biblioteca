import httpx
import reflex as rx
API="http://127.0.0.1:8765"
class POCState(rx.State):
 tela:str="catalogo"; perfil:str="visitante"; _token:str=""; livros:list[dict]=[]; busca:str=""; estado:str="Carregue o catálogo."; carregando:bool=False; mensagem:str=""; fila:list[dict]=[]
 def set_busca(self,value:str): self.busca=value
 @rx.var
 def livros_filtrados(self)->list[dict]:
  q=self.busca.lower().strip()
  return self.livros if not q else [b for b in self.livros if q in b["titulo"].lower() or q in b["autor"].lower() or q in b["categoria"].lower()]
 async def carregar_catalogo(self,modo="success"):
  self.carregando=True; self.estado="Carregando catálogo simulado…"; yield
  try:
   async with httpx.AsyncClient(timeout=3) as c:
    r=await c.get(f"{API}/catalog",params={"mode":modo}); r.raise_for_status(); self.livros=r.json()
   self.estado="Nenhum título encontrado." if not self.livros else f"{len(self.livros)} título(s) fictício(s)."
  except Exception as e: self.estado=f"Falha simulada: {type(e).__name__}"
  self.carregando=False
 async def entrar(self,perfil):
  try:
   async with httpx.AsyncClient(timeout=3) as c: r=await c.post(f"{API}/session",json={"perfil":perfil}); r.raise_for_status(); d=r.json()
   self._token=d["token"]; self.perfil=d["perfil"]; self.mensagem=f"Sessão fictícia: {self.perfil}."; self.tela="painel" if perfil=="bibliotecario" else "catalogo"
  except Exception as e: self.mensagem=f"Falha de sessão simulada: {type(e).__name__}"
 async def acao(self,path):
  h={"X-Demo-Session":self._token} if self._token else {}
  try:
   async with httpx.AsyncClient(timeout=3) as c: r=await (c.get(f"{API}{path}",headers=h) if path=="/reservations" else c.post(f"{API}{path}",headers=h))
   self.mensagem=f"HTTP {r.status_code}: {r.text}"
   if r.is_success and path=="/reservations": self.fila=r.json()
  except Exception as e: self.mensagem=f"API local indisponível: {type(e).__name__}"
 def ir(self,tela): self.tela=tela
 def sair(self): self._token=""; self.perfil="visitante"; self.mensagem="Sessão simulada encerrada."; self.tela="catalogo"
def card(b): return rx.card(rx.vstack(rx.heading(b["titulo"],size="4"),rx.text("Autor: ",b["autor"]),rx.text("Categoria: ",b["categoria"]),rx.text("Disponíveis (fixture): ",b["disponiveis"]),rx.button("Solicitar empréstimo (simulado)",on_click=POCState.acao("/loans/request")),rx.button("Reservar título (simulado)",on_click=POCState.ir("reservas")),align="start",spacing="2"),width="100%")
def catalogo(): return rx.vstack(rx.heading("Catálogo público",size="6"),rx.text("Fixtures fictícias; sem persistência ou regras reais."),rx.input(placeholder="Buscar título, autor ou categoria",value=POCState.busca,on_change=POCState.set_busca,width="100%"),rx.hstack(rx.button("Carregar",on_click=POCState.carregar_catalogo("success")),rx.button("Vazio",on_click=POCState.carregar_catalogo("empty")),rx.button("Erro",on_click=POCState.carregar_catalogo("error")),wrap="wrap"),rx.text(POCState.estado),rx.cond(POCState.carregando,rx.spinner(),rx.text("")),rx.foreach(POCState.livros_filtrados,card),spacing="4",width="100%",padding="1.5em")
def login(): return rx.vstack(rx.heading("Sessão e cadastro fictícios",size="6"),rx.text("Nenhuma conta ou senha é criada."),rx.button("Entrar como estudante fictício",on_click=POCState.entrar("estudante")),rx.button("Entrar como bibliotecário fictício",on_click=POCState.entrar("bibliotecario")),rx.text("Perfil atual: ",POCState.perfil),spacing="3",padding="1.5em")
def painel(): return rx.vstack(rx.heading("Painel bibliotecário simulado",size="6"),rx.text("Perfil atual: ",POCState.perfil),rx.button("Confirmar empréstimo (servidor verifica perfil)",on_click=POCState.acao("/loans/confirm")),rx.button("Ação administrativa (servidor verifica perfil)",on_click=POCState.acao("/admin/action")),rx.button("Trocar perfil",on_click=POCState.ir("login")),spacing="3",padding="1.5em")
def reservas(): return rx.vstack(rx.heading("Reserva e fila simuladas",size="6"),rx.button("Carregar fila fictícia",on_click=POCState.acao("/reservations")),rx.foreach(POCState.fila,lambda i:rx.text("Posição ",i["posicao"]," — ",i["titulo"])),rx.text("Sem FIFO real, prazo ou persistência."),spacing="3",padding="1.5em")
def body(): return rx.match(POCState.tela,("login",login()),("painel",painel()),("reservas",reservas()),catalogo())
def index(): return rx.vstack(rx.hstack(rx.heading("Biblioteca escolar · prova Reflex",size="5"),rx.spacer(),rx.button("Catálogo",on_click=POCState.ir("catalogo")),rx.button("Entrar / cadastrar",on_click=POCState.ir("login")),rx.button("Painel bibliotecário",on_click=POCState.ir("painel")),rx.button("Reservas / fila",on_click=POCState.ir("reservas")),rx.button("Sair",on_click=POCState.sair),width="100%",wrap="wrap",padding="1em"),rx.callout("PROVA DESCARTÁVEL · NÃO É FUNCIONALIDADE DO PRODUTO",icon="info",color_scheme="orange",width="100%"),rx.text(POCState.mensagem,role="status",aria_live="polite",padding_x="1em"),body(),width="100%",min_height="100vh",align="stretch",spacing="3")
app=rx.App(); app.add_page(index,route="/")
