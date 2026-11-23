import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { spawn } from "node:child_process";

const edge = String.raw`C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`;
const perfilTemp = fs.mkdtempSync(path.join(os.tmpdir(), "biblioteca-edge-"));
const capturaDir = path.join(process.cwd(), "docs", "capturas", "verificacao");
fs.mkdirSync(capturaDir, { recursive: true });

const rotas = [
  "/", "/login", "/cadastro", "/catalogo", "/catalogo/1",
  "/reservas", "/admin/acervo", "/admin/reservas", "/admin/bibliotecarios",
];
const larguras = [360, 768, 1366];
const temas = ["claro", "escuro"];
const perfis = ["visitante", "estudante", "bibliotecario", "admin"];
const linhas = [];
let violacoes = 0;

async function sleep(ms) {
  await new Promise((resolve) => setTimeout(resolve, ms));
}

async function launcher() {
  if (!fs.existsSync(edge)) {
    return { processo: null, motivo: "Edge não encontrado em " + edge };
  }
  const processo = spawn(edge, [
    "--headless=new",
    "--remote-debugging-port=9333",
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-gpu",
    `--user-data-dir=${perfilTemp}`,
    "about:blank",
  ], { stdio: "ignore" });
  for (let i = 0; i < 60; i++) {
    await sleep(500);
    try {
      const resposta = await fetch("http://127.0.0.1:9333/json");
      if (resposta.ok) return { processo, motivo: "" };
    } catch {}
  }
  processo.kill();
  return { processo: null, motivo: "Edge não respondeu ao remote debugging" };
}

class CDP {
  constructor(url) {
    this.url = url;
    this.nextId = 1;
    this.callbacks = new Map();
  }
  async connect() {
    this.ws = new WebSocket(this.url);
    await new Promise((resolve, reject) => {
      this.ws.onopen = resolve;
      this.ws.onerror = reject;
    });
    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.id && this.callbacks.has(message.id)) {
        const callback = this.callbacks.get(message.id);
        this.callbacks.delete(message.id);
        callback(message);
      }
    };
  }
  send(method, params = {}) {
    const id = this.nextId++;
    return new Promise((resolve) => {
      this.callbacks.set(id, resolve);
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }
  async eval(expression) {
    const response = await this.send("Runtime.evaluate", {
      expression,
      awaitPromise: true,
      returnByValue: true,
    });
    return response.result?.result?.value;
  }
  close() {
    this.ws?.close();
  }
}

async function navegar(cdp, url, timeout) {
  await cdp.send("Page.enable");
  await cdp.send("Runtime.enable");
  await cdp.send("Page.navigate", { url });
  for (let i = 0; i < timeout / 1000; i++) {
    await sleep(1000);
    const pronto = await cdp.eval(
      "({estado: document.readyState, texto: document.body?.innerText || '', corpo: !!document.querySelector('main, #root, [data-reflex-container]')})"
    );
    if (pronto?.estado === "complete" && (pronto?.texto || "").length > 200) return true;
  }
  return false;
}

async function verificarMatriz(cdp) {
  for (const rota of rotas) {
    for (const perfil of perfis) {
      for (const largura of larguras) {
        for (const tema of temas) {
          await cdp.send("Emulation.setDeviceMetricsOverride", {
            width: largura,
            height: largura >= 1024 ? 900 : 800,
            deviceScaleFactor: 1,
            mobile: largura < 768,
          });
          await cdp.eval(`localStorage.setItem('biblioteca-theme','${tema === "escuro" ? "dark" : "light"}'); document.documentElement.dataset.theme='${tema === "escuro" ? "dark" : "light"}'`);
          if (perfil !== "visitante") {
            const contas = {
              estudante: ["demo.estudante@example.invalid", "demo123"],
              bibliotecario: ["demo.bibliotecario@example.invalid", "demo123"],
              admin: ["demo.admin@example.invalid", "demo123"],
            };
            await navegar(cdp, "http://localhost:3000/login", 60000);
            await cdp.eval(`(() => {
              const [email, senha] = ${JSON.stringify(contas[perfil])};
              const inputs = [...document.querySelectorAll('input')];
              const emailInput = inputs.find(e => e.type === 'email' || /email/i.test(e.getAttribute('aria-label') || e.name || e.placeholder || ''));
              const senhaInput = inputs.find(e => e.type === 'password');
              const setValue = (el, value) => {
                const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')?.set;
                setter?.call(el, value);
                el.dispatchEvent(new Event('input', {bubbles:true}));
                el.dispatchEvent(new Event('change', {bubbles:true}));
              };
              if (emailInput) setValue(emailInput, email);
              if (senhaInput) setValue(senhaInput, senha);
              const botao = [...document.querySelectorAll('button')].find(e => /entrar/i.test(e.innerText));
              botao?.click();
              return !!emailInput && !!senhaInput;
            })()`);
            await sleep(3000);
          }
          const hidratou = await navegar(
            cdp,
            `http://localhost:3000${rota}`,
            linhaContexto(rota) ? 300000 : 60000,
          );
          const resultado = await cdp.eval(`(() => {
            const erros = !!document.body.innerText.includes('Connection Error') || !!document.body.innerText.includes('An error occurred while rendering');
            const headers = [...document.querySelectorAll('header')];
            const navs = headers.flatMap(h => [...h.querySelectorAll('nav')]);
            const menus = [...document.querySelectorAll('.site-menu-toggle')].filter(e => getComputedStyle(e).display !== 'none');
            const horizontal = document.documentElement.scrollWidth > document.documentElement.clientWidth + 1;
            const h = headers[0] ? headers[0].getBoundingClientRect().height : 0;
            const texto = document.body.innerText || '';
            const sobreposicoes = (() => {
              const seletores = 'a,button,input,select,textarea,h1,h2,h3,img,article';
              const itens = [...document.querySelectorAll(seletores)].filter(e => {
                const r=e.getBoundingRect?.() || e.getBoundingClientRect();
                const s=getComputedStyle(e);
                return s.visibility !== 'hidden' && s.display !== 'none' && r.width>0 && r.height>0;
              });
              let pares=[];
              for(let i=0;i<itens.length;i++) for(let j=i+1;j<itens.length;j++){
                const a=itens[i].getBoundingClientRect(), b=itens[j].getBoundingClientRect();
                if(a.left<b.right && b.left<a.right && a.top<b.bottom && b.top<a.bottom){
                  if(!itens[i].contains(itens[j]) && !itens[j].contains(itens[i])) pares.push([itens[i].tagName,itens[j].tagName]);
                }
              }
              return pares.length;
            })();
            const rgb = value => { const m=(value||'').match(/[0-9]+/g); return m ? m.slice(0,3).map(Number) : [0,0,0]; };
            const luminancia = c => { const v=c.map(x=>{x/=255; return x<=0.04045?x/12.92:((x+0.055)/1.055)**2.4}); return 0.2126*v[0]+0.7152*v[1]+0.0722*v[2]; };
            const contraste = (fg,bg) => { const a=luminancia(rgb(fg)), b=luminancia(rgb(bg)); return (Math.max(a,b)+0.05)/(Math.min(a,b)+0.05); };
            let contrasteViolacoes=0;
            for(const el of [...document.querySelectorAll('button,a,label')]){
              const s=getComputedStyle(el); let fundo=s.backgroundColor, pai=el;
              while(pai && (fundo==='rgba(0, 0, 0, 0)'||fundo==='transparent')){ pai=pai.parentElement; fundo=pai?getComputedStyle(pai).backgroundColor:'rgb(255,255,255)'; }
              const grande=parseFloat(s.fontSize)>=24 || (parseFloat(s.fontSize)>=18.66 && Number(s.fontWeight)>=700);
              if(getComputedStyle(el).display!=='none' && el.getBoundingClientRect().height>0 && contraste(s.color,fundo)<(grande?3:4.5)) contrasteViolacoes++;
            }
            const alvos = [...document.querySelectorAll('button,a')].filter(e=>getComputedStyle(e).display!=='none');
            const alvosBaixos = alvos.filter(e=>e.getBoundingClientRect().height>0 && e.getBoundingClientRect().height<44).length;
            return {erros, headers:headers.length, navs:navs.length, menus:menus.length, horizontal, h, sobreposicoes, texto:texto.length, contrasteViolacoes, alvosBaixos};
          })()`);
          const problemas = [];
          if (!hidratou) problemas.push("hidratação");
          if (resultado?.erros) problemas.push("erro de rendering");
          if (resultado?.headers !== 1) problemas.push("cabeçalhos=" + resultado?.headers);
          if (resultado?.navs !== 1) problemas.push("navegações=" + resultado?.navs);
          if (resultado?.menus !== 0) problemas.push("menus duplicados=" + resultado?.menus);
          if (resultado?.horizontal) problemas.push("rolagem horizontal");
          if (resultado?.sobreposicoes) problemas.push("sobreposições=" + resultado?.sobreposicoes);
          if (resultado?.contrasteViolacoes) problemas.push("contraste=" + resultado?.contrasteViolacoes);
          if (resultado?.alvosBaixos) problemas.push("alvos baixos=" + resultado?.alvosBaixos);
          if (largura >= 1024 && resultado?.h > 80) problemas.push("cabeçalho alto");
          if (largura === 360 && resultado?.h > 150) problemas.push("cabeçalho móvel alto");

          if (problemas.length) violacoes += problemas.length;
          const nomeRota = rota === "/" ? "home" : rota.replaceAll("/", "-").replace(/^-/, "");
          const nome = `${nomeRota}-${perfil}-${largura}-${tema}.png`;
          const captura = await cdp.send("Page.captureScreenshot", { format: "png", captureBeyondViewport: false });
          const shot = await cdp.eval("document.title");
          linhas.push(`| ${rota} | ${perfil} | ${largura} | ${tema} | ${problemas.length ? "FALHOU" : "PASSOU"} | ${problemas.join("; ") || "nenhuma"} |`);
          const caminho = path.join(capturaDir, nome);
          if (captura?.result?.data) {
            fs.writeFileSync(caminho, Buffer.from(captura.result.data, "base64"));
          } else {
            fs.writeFileSync(caminho + ".json", JSON.stringify({ title: shot, route: rota, profile: perfil, width: largura, theme: tema }));
          }
        }
      }
    }
  }
}

function linhaContexto(rota) {
  return rota === "/" || rota === "/login";
}

async function main() {
  const saida = await launcher();
  if (saida.motivo) {
    fs.writeFileSync(path.join(process.cwd(), "docs", "verificacao-layout.md"),
      `# Verificação de layout\n\nEdge não pôde ser dirigido: ${saida.motivo}. Resultado visual: não verificado.\n`);
    console.log("FALHOU: " + saida.motivo);
    process.exitCode = 1;
    return;
  }
  await sleep(1000);
  const paginas = await (await fetch("http://127.0.0.1:9333/json")).json();
  const cdp = new CDP(paginas[0].webSocketDebuggerUrl);
  await cdp.connect();
  await verificarMatriz(cdp);
  cdp.close();
  saida.processo.kill();

  fs.writeFileSync(path.join(process.cwd(), "docs", "verificacao-layout.md"),
    `# Verificação de layout\n\n| rota | perfil | largura | tema | resultado | violações |\n|---|---|---:|---|---|---|\n${linhas.join("\n")}\n`);
  console.log(violacoes ? `FALHOU: ${violacoes} violações` : "PASSOU: zero violações");
  process.exitCode = violacoes ? 1 : 0;
}

main();
