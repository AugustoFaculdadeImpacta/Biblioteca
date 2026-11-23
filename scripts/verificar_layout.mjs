import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { execFileSync, spawn } from "node:child_process";

const baseUrl = "http://localhost:3000";
const edgeCandidates = [
  String.raw`C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`,
  String.raw`C:\Program Files\Microsoft\Edge\Application\msedge.exe`,
];
const visitorRoutes = ["/", "/catalogo", "/catalogo/1", "/login", "/cadastro"];
const widths = [360, 1366];
const themes = ["claro", "escuro"];
const reportPath = path.join(process.cwd(), "docs", "verificacao-layout.md");
const captureDir = path.join(
  process.cwd(),
  "docs",
  "capturas",
  "verificacao",
);
const totalLimitMs = 20 * 60 * 1000;
const startedAt = Date.now();
const deadline = startedAt + totalLimitMs;
const firstLoads = new Set();
const recorded = new Set();
const matrix = [];
let failures = 0;

for (const route of visitorRoutes) {
  for (const width of widths) {
    for (const theme of themes) {
      matrix.push({ route, profile: "visitante", width, theme });
    }
  }
}

for (const group of [
  { profile: "estudante", routes: ["/reservas"] },
  { profile: "bibliotecario", routes: ["/admin/acervo", "/admin/reservas"] },
  { profile: "admin", routes: ["/admin/bibliotecarios"] },
]) {
  for (const route of group.routes) {
    for (const width of [1366, 360]) {
      matrix.push({ route, profile: group.profile, width, theme: "escuro" });
    }
  }
}

function appendReportHeader() {
  fs.mkdirSync(path.dirname(reportPath), { recursive: true });
  fs.mkdirSync(captureDir, { recursive: true });
  fs.appendFileSync(
    reportPath,
    `\n## Rodada ${new Date().toISOString()}\n\n` +
      "| rota | perfil | largura | tema | resultado | violações | captura |\n" +
      "|---|---|---:|---|---|---|---|\n",
    "utf8",
  );
}

function slug(route) {
  return route === "/" ? "home" : route.replaceAll("/", "-").replace(/^-/, "");
}

function capturePath(combo) {
  return path.join(
    captureDir,
    `${slug(combo.route)}-${combo.profile}-${combo.width}-${combo.theme}.png`,
  );
}

function cleanCell(value) {
  return String(value ?? "nenhuma").replaceAll("|", "\\|").replaceAll("\n", " ");
}

function appendResult(combo, status, violations, imagePath = "") {
  const image = imagePath
    ? `[PNG](./capturas/verificacao/${path.basename(imagePath)})`
    : "não disponível";
  const row =
    `| ${combo.route} | ${combo.profile} | ${combo.width} | ${combo.theme} | ` +
    `${status} | ${cleanCell(violations.join("; ") || "nenhuma")} | ${image} |\n`;
  fs.appendFileSync(reportPath, row, "utf8");
  recorded.add(`${combo.route}|${combo.profile}|${combo.width}|${combo.theme}`);
  if (status !== "PASSOU") failures++;
  console.log(
    `${status}: ${combo.route} / ${combo.profile} / ${combo.width} / ${combo.theme}`,
  );
}

function remainingMs() {
  return Math.max(0, deadline - Date.now());
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function terminateEdge(edgeProcess) {
  if (edgeProcess && edgeProcess.exitCode === null) {
    edgeProcess.kill();
    await Promise.race([
      new Promise((resolve) => edgeProcess.once("exit", resolve)),
      sleep(5000),
    ]);
  }
  if (edgeProcess && edgeProcess.exitCode === null) {
    throw new Error("Edge não encerrou pelo PID iniciado pelo robô");
  }
}

class CdpConnection {
  constructor(url) {
    this.url = url;
    this.nextId = 1;
    this.pending = new Map();
  }

  async connect(timeoutMs) {
    this.socket = new WebSocket(this.url);
    await new Promise((resolve, reject) => {
      const timer = setTimeout(
        () => reject(new Error("conexão CDP excedeu o tempo limite")),
        timeoutMs,
      );
      this.socket.addEventListener("open", () => {
        clearTimeout(timer);
        resolve();
      }, { once: true });
      this.socket.addEventListener("error", () => {
        clearTimeout(timer);
        reject(new Error("não foi possível conectar ao CDP"));
      }, { once: true });
    });
    this.socket.addEventListener("message", (event) => {
      const message = JSON.parse(event.data);
      if (!message.id || !this.pending.has(message.id)) return;
      const pending = this.pending.get(message.id);
      this.pending.delete(message.id);
      clearTimeout(pending.timer);
      if (message.error) {
        pending.reject(new Error("comando CDP falhou"));
      } else {
        pending.resolve(message);
      }
    });
    this.socket.addEventListener("close", () => {
      for (const pending of this.pending.values()) {
        clearTimeout(pending.timer);
        pending.reject(new Error("conexão CDP encerrada"));
      }
      this.pending.clear();
    });
  }

  send(method, params = {}, timeoutMs = 10000) {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      return Promise.reject(new Error("conexão CDP indisponível"));
    }
    const id = this.nextId++;
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        this.pending.delete(id);
        reject(new Error("comando CDP excedeu o tempo limite"));
      }, timeoutMs);
      this.pending.set(id, { resolve, reject, timer });
      this.socket.send(JSON.stringify({ id, method, params }));
    });
  }

  async evaluate(expression, timeoutMs = 10000) {
    const response = await this.send(
      "Runtime.evaluate",
      { expression, awaitPromise: true, returnByValue: true },
      timeoutMs,
    );
    if (response.result?.exceptionDetails) {
      throw new Error("avaliação da página falhou");
    }
    return response.result?.result?.value;
  }

  close() {
    if (this.socket?.readyState === WebSocket.OPEN) this.socket.close();
  }
}

async function launchEdge() {
  const executable = edgeCandidates.find((candidate) =>
    fs.existsSync(candidate)
  );
  if (!executable) throw new Error("Edge não encontrado");

  const profileDir = fs.mkdtempSync(
    path.join(os.tmpdir(), "biblioteca-layout-"),
  );
  const activePortFile = path.join(profileDir, "DevToolsActivePort");
  let edgeProcess;
  try {
    edgeProcess = spawn(
      executable,
      [
        "--headless=new",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-gpu",
        "--disable-extensions",
        `--user-data-dir=${profileDir}`,
        "--remote-debugging-port=0",
        "about:blank",
      ],
      { stdio: "ignore", windowsHide: true },
    );
  } catch (error) {
    fs.rmSync(profileDir, { recursive: true, force: true });
    throw error;
  }

  const launchDeadline = Math.min(Date.now() + 30000, deadline);
  let debugPort = 0;
  let version;
  while (Date.now() < launchDeadline) {
    if (edgeProcess.exitCode !== null) {
      fs.rmSync(profileDir, { recursive: true, force: true });
      throw new Error("Edge encerrou antes de iniciar o CDP");
    }
    if (fs.existsSync(activePortFile)) {
      const activePort = fs.readFileSync(activePortFile, "utf8").split(/\r?\n/)[0];
      debugPort = Number(activePort);
      if (Number.isInteger(debugPort) && debugPort > 0) {
        try {
          const response = await fetch(
            `http://127.0.0.1:${debugPort}/json/version`,
          );
          if (response.ok) {
            version = await response.json();
            break;
          }
        } catch {
          await sleep(250);
        }
      }
    }
    await sleep(250);
  }
  if (!version?.webSocketDebuggerUrl) {
    await terminateEdge(edgeProcess);
    fs.rmSync(profileDir, {
      recursive: true,
      force: true,
      maxRetries: 5,
      retryDelay: 500,
    });
    throw new Error("Edge não respondeu ao CDP");
  }

  return {
    process: edgeProcess,
    pid: edgeProcess.pid,
    profileDir,
    debugPort,
    browserUrl: version.webSocketDebuggerUrl,
  };
}

function loadDemoAccounts() {
  const timeout = Math.min(10000, remainingMs());
  if (timeout <= 0) throw new Error("limite total atingido");
  const python = path.join(
    process.cwd(),
    ".venv",
    "Scripts",
    "python.exe",
  );
  const source =
    "import json; " +
    "from scripts.demo_seed_data import DEMO_USERS; " +
    "from scripts.demo_api import PASSWORD; " +
    "print(json.dumps({'users': [{'perfil': u['perfil'], 'email': u['email']} " +
    "for u in DEMO_USERS], 'password': PASSWORD}))";
  const output = execFileSync(python, ["-c", source], {
    cwd: process.cwd(),
    encoding: "utf8",
    stdio: ["ignore", "pipe", "ignore"],
    windowsHide: true,
    timeout,
  });
  return JSON.parse(output);
}

async function setViewportAndTheme(cdp, combo, priorScriptId) {
  const commandTimeout = () => Math.max(1, Math.min(5000, remainingMs()));
  await cdp.send("Emulation.setDeviceMetricsOverride", {
    width: combo.width,
    height: combo.width >= 1024 ? 900 : 800,
    deviceScaleFactor: 1,
    mobile: combo.width < 768,
  }, commandTimeout());
  await cdp.send("Emulation.setEmulatedMedia", {
    features: [
      {
        name: "prefers-color-scheme",
        value: combo.theme === "escuro" ? "dark" : "light",
      },
    ],
  }, commandTimeout());
  if (priorScriptId) {
    await cdp.send("Page.removeScriptToEvaluateOnNewDocument", {
      identifier: priorScriptId,
    }, commandTimeout());
  }
  const preference = JSON.stringify({
    theme: combo.theme === "escuro" ? "dark" : "light",
    fontScale: 100,
    highContrast: false,
    reduceMotion: false,
  });
  const script = `localStorage.setItem("biblioteca-aparencia", ${JSON.stringify(preference)});`;
  const response = await cdp.send("Page.addScriptToEvaluateOnNewDocument", {
    source: script,
  }, commandTimeout());
  return response.result.identifier;
}

async function navigate(cdp, route) {
  const firstLoad = !firstLoads.has(route);
  firstLoads.add(route);
  const budget = firstLoad ? 300000 : 90000;
  const timeoutMs = Math.min(budget, remainingMs());
  if (timeoutMs <= 0) return { hydrated: false, timedOut: true };
  const end = Date.now() + timeoutMs;

  try {
    await cdp.send(
      "Page.navigate",
      { url: `${baseUrl}${route}` },
      Math.min(10000, timeoutMs),
    );
    while (Date.now() < end && remainingMs() > 0) {
      const state = await cdp.evaluate(
        "({ready:document.readyState,text:(document.body?.innerText||'').length})",
        Math.min(5000, end - Date.now(), remainingMs()),
      );
      if (state?.ready === "complete" && state.text > 200) {
        return { hydrated: true, timedOut: false };
      }
      await sleep(Math.min(400, Math.max(0, end - Date.now())));
    }
    return { hydrated: false, timedOut: true };
  } catch {
    return { hydrated: false, timedOut: Date.now() >= end || remainingMs() === 0 };
  }
}

async function inspectPage(cdp, timeoutMs) {
  return cdp.evaluate(`(() => {
    const visible = (el) => {
      const style = getComputedStyle(el);
      const rect = el.getBoundingClientRect();
      return style.display !== "none" &&
        style.visibility !== "hidden" &&
        Number(style.opacity) > 0 &&
        rect.width > 0 &&
        rect.height > 0;
    };
    const describe = (el) => {
      const classes = [...el.classList].filter(Boolean).join(".");
      return el.tagName.toLowerCase() + (classes ? "." + classes : "");
    };
    const onScreen = (el) => {
      if (!visible(el) || el.matches(".skip-link")) return false;
      const rect = el.getBoundingClientRect();
      return rect.right > 0 && rect.bottom > 0 &&
        rect.left < innerWidth && rect.top < innerHeight;
    };
    const headers = [...document.querySelectorAll("header")];
    const headerHeight = headers[0]?.getBoundingClientRect().height || 0;
    const text = document.body?.innerText || "";
    const errors =
      /Connection Error|Cannot connect to server|An error occurred/i.test(text);
    const loading = /\bCarregando\b/i.test(text);
    const width = Math.max(
      document.documentElement.scrollWidth,
      document.body?.scrollWidth || 0,
    );
    const clientWidth = document.documentElement.clientWidth;
    const parseColor = (value) => {
      const values = (value.match(/[\\d.]+/g) || []).map(Number);
      if (values.length < 3) return null;
      return [values[0], values[1], values[2], values.length > 3 ? values[3] : 1];
    };
    const blend = (front, back) => front.map((value, index) =>
      value * front[3] + back[index] * (1 - front[3])
    ).concat(1);
    const backgroundFor = (el) => {
      let background = [255, 255, 255, 1];
      const chain = [];
      for (let node = el; node; node = node.parentElement) chain.push(node);
      for (const node of chain.reverse()) {
        const color = parseColor(getComputedStyle(node).backgroundColor);
        if (color && color[3] > 0) background = blend(color, background);
      }
      return background;
    };
    const luminance = (color) => {
      const channels = color.slice(0, 3).map((value) => {
        value /= 255;
        return value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4;
      });
      return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2];
    };
    const contrastFailures = [];
    for (const element of document.querySelectorAll("button, a")) {
      if (!visible(element) || element.matches(".skip-link")) continue;
      const style = getComputedStyle(element);
      const foreground = parseColor(style.color);
      if (!foreground) {
        contrastFailures.push(describe(element));
        continue;
      }
      const actualForeground = blend(foreground, backgroundFor(element));
      const actualBackground = backgroundFor(element);
      const first = luminance(actualForeground);
      const second = luminance(actualBackground);
      const ratio = (Math.max(first, second) + 0.05) /
        (Math.min(first, second) + 0.05);
      if (ratio < 4.5) contrastFailures.push(describe(element));
    }
    const smallTargets = [];
    for (const element of document.querySelectorAll("button, a")) {
      if (!visible(element) || element.matches(".skip-link")) continue;
      const rect = element.getBoundingClientRect();
      if (rect.width < 44 || rect.height < 44) {
        smallTargets.push(describe(element));
      }
    }
    const flowOverlaps = [];
    const parents = [
      ...document.querySelectorAll(
        "main, .app-shell, .content-section, .home-book-section-content, " +
        ".student-library-section, .admin-acervo-content, .admin-catalog-section, " +
        ".librarian-management-section",
      ),
    ];
    for (const parent of parents) {
      if (!visible(parent)) continue;
      const style = getComputedStyle(parent);
      const singleGridColumn =
        style.display === "grid" &&
        style.gridTemplateColumns.trim().split(/\\s+/).length === 1;
      const verticalFlow =
        parent.tagName === "MAIN" ||
        parent.classList.contains("app-shell") ||
        (style.display === "flex" && style.flexDirection === "column") ||
        singleGridColumn;
      if (!verticalFlow) continue;
      const children = [...parent.children].filter((child) => {
        if (!visible(child) || child.matches(".skip-link")) return false;
        const position = getComputedStyle(child).position;
        return position !== "absolute" && position !== "fixed";
      });
      for (let index = 0; index < children.length - 1; index++) {
        const first = children[index].getBoundingClientRect();
        const next = children[index + 1].getBoundingClientRect();
        if (first.bottom > next.top + 1) {
          flowOverlaps.push(
            describe(parent) +
              ":" +
              describe(children[index]) +
              "->" +
              describe(children[index + 1]),
          );
        }
      }
    }
    const overflowChildren = [];
    for (const child of document.querySelectorAll("body *")) {
      if (!visible(child) || child.matches(".skip-link")) continue;
      const parent = child.parentElement;
      if (!parent || !visible(parent)) continue;
      if (child.closest(".profile-menu-content, .accessibility-menu-content")) continue;
      const parentStyle = getComputedStyle(parent);
      if (["auto", "scroll"].includes(parentStyle.overflowX) ||
          ["auto", "scroll"].includes(parentStyle.overflowY)) continue;
      const childRect = child.getBoundingClientRect();
      const parentRect = parent.getBoundingClientRect();
      if (childRect.right > parentRect.right + 1 ||
          childRect.bottom > parentRect.bottom + 1) {
        overflowChildren.push(describe(child) + ">" + describe(parent));
      }
    }
    return {
      errors,
      loading,
      bodyLength: text.length,
      headers: headers.length,
      headerHeight,
      horizontal: width > clientWidth + 1,
      contrastFailures,
      smallTargets,
      flowOverlaps,
      overflowChildren,
      path: location.pathname,
    };
  })()`, timeoutMs);
}

async function saveScreenshot(cdp, combo) {
  if (remainingMs() <= 0) return "";
  const response = await cdp.send(
    "Page.captureScreenshot",
    { format: "png", captureBeyondViewport: false },
    Math.min(10000, remainingMs()),
  );
  const data = response.result?.data;
  if (!data) return "";
  const output = capturePath(combo);
  fs.writeFileSync(output, Buffer.from(data, "base64"));
  return output;
}

async function runCombo(cdp, combo, priorScriptId, setupViolation = "") {
  const violations = [];
  if (setupViolation) violations.push(setupViolation);
  let scriptId = priorScriptId;
  let navigation = { hydrated: false, timedOut: false };
  let imagePath = "";

  try {
    scriptId = await setViewportAndTheme(cdp, combo, priorScriptId);
    navigation = await navigate(cdp, combo.route);
    if (navigation.timedOut) {
      violations.push("TEMPO ESGOTADO");
    } else if (!navigation.hydrated) {
      violations.push("hidratação");
    }
    if (!navigation.timedOut && navigation.hydrated && remainingMs() > 0) {
      await sleep(Math.min(12000, remainingMs()));
      if (remainingMs() <= 0) {
        violations.push("TEMPO ESGOTADO");
      } else {
        const result = await inspectPage(
          cdp,
          Math.min(10000, remainingMs()),
        );
        if (result.errors || result.bodyLength <= 200) {
          violations.push("erro de conexão/renderização ou corpo menor que 200 caracteres");
        }
        if (result.loading) violations.push("conteúdo ainda carregando");
        if (result.path !== combo.route) {
          violations.push(`redirecionado para ${result.path}`);
        }
        if (result.headers !== 1) violations.push(`cabeçalhos=${result.headers}`);
        if (combo.width >= 1024 && result.headerHeight > 80) {
          violations.push(`cabeçalho=${Math.round(result.headerHeight)}px`);
        }
        if (result.horizontal) violations.push("rolagem horizontal da página");
        if (result.flowOverlaps.length) {
          violations.push(`sobreposição vertical=${result.flowOverlaps.join(",")}`);
        }
        if (result.overflowChildren.length) {
          violations.push(`filhos fora do contêiner=${result.overflowChildren.join(",")}`);
        }
        if (result.contrastFailures.length) {
          violations.push(`contraste abaixo de 4,5:1=${result.contrastFailures.join(",")}`);
        }
        if (result.smallTargets.length) {
          violations.push(`alvos menores que 44px=${result.smallTargets.join(",")}`);
        }
      }
    }
  } catch {
    violations.push("erro de navegação ou inspeção");
  }

  try {
    imagePath = await saveScreenshot(cdp, combo);
  } catch {
    imagePath = "";
  }
  if (!imagePath) {
    violations.push("captura PNG ausente");
    if (remainingMs() <= 0 && !violations.includes("TEMPO ESGOTADO")) {
      violations.push("TEMPO ESGOTADO");
    }
  }

  const timedOut = violations.includes("TEMPO ESGOTADO");
  const status = timedOut
    ? "TEMPO ESGOTADO"
    : violations.length
      ? "FALHOU"
      : "PASSOU";
  appendResult(combo, status, violations, imagePath);
  return scriptId;
}

async function login(cdp, account, password) {
  const navigation = await navigate(cdp, "/login");
  if (!navigation.hydrated) return false;
  const values = await cdp.evaluate(`(() => {
    const email = document.querySelector("#login-email");
    const senha = document.querySelector("#login-senha");
    const botao = document.querySelector("#form-login button[type='submit']");
    if (!email || !senha || !botao) return false;
    const setter = Object.getOwnPropertyDescriptor(
      HTMLInputElement.prototype, "value"
    ).set;
    setter.call(email, ${JSON.stringify(account.email)});
    setter.call(senha, ${JSON.stringify(password)});
    email.dispatchEvent(new Event("input", { bubbles: true }));
    senha.dispatchEvent(new Event("input", { bubbles: true }));
    email.dispatchEvent(new Event("change", { bubbles: true }));
    senha.dispatchEvent(new Event("change", { bubbles: true }));
    botao.click();
    return true;
  })()`);
  if (!values) return false;

  const end = Math.min(Date.now() + 90000, deadline);
  while (Date.now() < end && remainingMs() > 0) {
    const authenticated = await cdp.evaluate(
      `location.pathname !== "/login" && ` +
        `!!document.querySelector("details.profile-menu") && ` +
        `/Sair/.test(document.querySelector("details.profile-menu").textContent)`,
      Math.min(5000, end - Date.now(), remainingMs()),
    );
    if (authenticated) return true;
    await sleep(400);
  }
  return false;
}

async function logout(cdp) {
  const clicked = await cdp.evaluate(`(() => {
    const menu = document.querySelector("details.profile-menu");
    if (!menu) return false;
    menu.open = true;
    const button = [...menu.querySelectorAll("button")].find((item) =>
      /Sair/.test(item.innerText)
    );
    if (!button) return false;
    button.click();
    return true;
  })()`);
  if (!clicked) return false;
  const end = Math.min(Date.now() + 30000, deadline);
  while (Date.now() < end && remainingMs() > 0) {
    const signedOut = await cdp.evaluate(
      `!document.querySelector("details.profile-menu") || ` +
        `!/Sair/.test(document.querySelector("details.profile-menu").textContent)`,
      Math.min(5000, end - Date.now(), remainingMs()),
    );
    if (signedOut) return true;
    await sleep(300);
  }
  return false;
}

function recordUnattempted(combos, status, reason) {
  for (const combo of combos) {
    appendResult(combo, status, [reason]);
  }
}

async function main() {
  appendReportHeader();
  let edge;
  let browserConnection;
  let pageConnection;
  let scriptId = "";
  try {
    edge = await launchEdge();
    browserConnection = new CdpConnection(edge.browserUrl);
    await browserConnection.connect(Math.min(15000, remainingMs()));
    const listResponse = await fetch(
      `http://127.0.0.1:${edge.debugPort}/json/list`,
    );
    const targets = await listResponse.json();
    const page = targets.find((target) => target.type === "page");
    if (!page?.webSocketDebuggerUrl) throw new Error("aba do Edge indisponível");
    pageConnection = new CdpConnection(page.webSocketDebuggerUrl);
    await pageConnection.connect(Math.min(15000, remainingMs()));
    await pageConnection.send("Page.enable");
    await pageConnection.send("Runtime.enable");
    await pageConnection.send("Network.enable");

    const visitorCombos = matrix.filter(
      (combo) => combo.profile === "visitante",
    );
    for (const combo of visitorCombos) {
      if (remainingMs() <= 0) {
        appendResult(combo, "TEMPO ESGOTADO", ["limite total de 20 minutos"]);
        continue;
      }
      scriptId = await runCombo(pageConnection, combo, scriptId);
    }

    let demo;
    let accountError = false;
    try {
      demo = loadDemoAccounts();
    } catch {
      accountError = true;
    }

    const profileGroups = [
      { profile: "estudante", routes: ["/reservas"] },
      { profile: "bibliotecario", routes: ["/admin/acervo", "/admin/reservas"] },
      { profile: "admin", routes: ["/admin/bibliotecarios"] },
    ];
    for (const group of profileGroups) {
      const account = demo?.users?.find(
        (user) => user.perfil === group.profile,
      );
      let authenticated = false;
      if (remainingMs() > 0 && account && !accountError) {
        authenticated = await login(pageConnection, account, demo.password);
      }

      const groupCombos = matrix.filter(
        (combo) =>
          combo.profile === group.profile && group.routes.includes(combo.route),
      );
      for (const combo of groupCombos) {
        const setupViolation = authenticated
          ? ""
          : accountError || !account
            ? "conta de demonstração indisponível"
            : "autenticação do perfil falhou";
        if (remainingMs() <= 0) {
          appendResult(combo, "TEMPO ESGOTADO", ["limite total de 20 minutos"]);
          continue;
        }
        scriptId = await runCombo(
          pageConnection,
          combo,
          scriptId,
          setupViolation,
        );
      }

      if (authenticated && remainingMs() > 0) {
        const signedOut = await logout(pageConnection);
        if (!signedOut) {
          await pageConnection.send("Network.clearBrowserCookies");
          await pageConnection.send("Storage.clearDataForOrigin", {
            origin: baseUrl,
            storageTypes: "all",
          });
        }
      }
    }

  } catch {
    const remaining = matrix.filter(
      (combo) =>
        !recorded.has(
          `${combo.route}|${combo.profile}|${combo.width}|${combo.theme}`,
        ),
    );
    const status = remainingMs() === 0 ? "TEMPO ESGOTADO" : "NÃO VERIFICADO";
    const reason = remainingMs() === 0
      ? "limite total de 20 minutos"
      : "Edge não conseguiu executar a matriz";
    recordUnattempted(remaining, status, reason);
  } finally {
    if (pageConnection) pageConnection.close();
    if (browserConnection) {
      try {
        await browserConnection.send("Browser.close", {}, 3000);
      } catch {}
      browserConnection.close();
    }
    if (edge?.profileDir) {
      try {
        await terminateEdge(edge.process);
        if (fs.existsSync(edge.profileDir)) {
          fs.rmSync(edge.profileDir, {
            recursive: true,
            force: true,
            maxRetries: 5,
            retryDelay: 500,
          });
        }
      } catch {
        failures++;
        process.stderr.write("Falha ao encerrar o Edge próprio do robô.\n");
      }
    }
    const duration = Math.round((Date.now() - startedAt) / 1000);
    fs.appendFileSync(
      reportPath,
      `\nDuração desta rodada: ${duration}s. Limite total: 1200s.\n`,
      "utf8",
    );
    process.exitCode = failures ? 1 : 0;
  }
}

main();
