// Carregador da versão do Trilha que roda no navegador.
//
// 1. Carrega o Pyodide, instala o Django e as dependências (wheels publicadas junto com o site)
//    e descompacta o código do projeto.
// 2. Monta /dados sobre o IndexedDB, onde fica o SQLite, e roda as migrations.
// 3. Cada navegação, envio de formulário ou fetch da página vira uma requisição WSGI para o
//    Django (navegador/ponte.py), e o HTML devolvido é escrito no iframe.
//
// A rota atual fica no hash (#/trilha/), para que recarregar a página mantenha o lugar.

(function () {
  "use strict";

  const BASE = new URL(".", location.href);           // .../gcc265-trilha-django/
  const STATIC_URL = BASE.pathname + "static/";
  const CHAVE_COOKIES = "trilha-cookies";
  const iframe = document.getElementById("pagina");
  const etapa = document.getElementById("etapa");
  let pyodide, ponte, FS;
  let fila = Promise.resolve();                        // uma requisição por vez

  // ---------- cookies (sessão e CSRF do Django) ----------

  function lerCookies() {
    try { return JSON.parse(localStorage.getItem(CHAVE_COOKIES)) || {}; } catch (e) { return {}; }
  }
  let cookies = lerCookies();

  function guardarCookies() {
    try { localStorage.setItem(CHAVE_COOKIES, JSON.stringify(cookies)); } catch (e) { /* sem storage */ }
  }

  function aplicarSetCookie(valor) {
    const partes = valor.split(";").map((p) => p.trim());
    const [nome, ...resto] = partes[0].split("=");
    const conteudo = resto.join("=");
    const atributos = partes.slice(1).map((p) => p.toLowerCase());
    const expirado = atributos.some((a) => a === "max-age=0" || a.startsWith("expires=thu, 01 jan 1970"));
    if (expirado || conteudo === '""') delete cookies[nome]; else cookies[nome] = conteudo;
    guardarCookies();
  }

  function cabecalhoCookie() {
    return Object.entries(cookies).map(([n, v]) => n + "=" + v).join("; ");
  }

  // ---------- requisição ao Django ----------

  function ehRotaDoDjango(url) {
    return url.origin === location.origin && !url.pathname.startsWith(STATIC_URL) &&
           !url.pathname.startsWith(BASE.pathname + "wheels/");
  }

  function caminhoDjango(url) {
    // Links gerados pelo Django são absolutos a partir da raiz (/trilha/); os que caem dentro
    // da pasta do site no Pages (/gcc265-trilha-django/trilha/) também são aceitos.
    let caminho = url.pathname;
    if (caminho.startsWith(BASE.pathname)) caminho = "/" + caminho.slice(BASE.pathname.length);
    return caminho;
  }

  async function sincronizarBanco() {
    await new Promise((ok, falha) => FS.syncfs(false, (erro) => (erro ? falha(erro) : ok())));
  }

  function requisitar(metodo, caminho, consulta, corpo, tipo) {
    const tarefa = fila.then(async () => {
      const r = ponte.requisitar(metodo, caminho, consulta || "", corpo || "", tipo || "", cabecalhoCookie())
        .toJs({ dict_converter: Object.fromEntries });
      const cabecalhos = {};
      for (const [nome, valor] of r.cabecalhos) {
        if (nome.toLowerCase() === "set-cookie") aplicarSetCookie(valor);
        else cabecalhos[nome.toLowerCase()] = valor;
      }
      if (metodo !== "GET") await sincronizarBanco();
      return { status: r.status, cabecalhos, corpo: r.corpo };
    });
    fila = tarefa.catch(() => {});
    return tarefa;
  }

  // ---------- navegação ----------

  async function navegar(metodo, alvo, corpo, tipo, empurrarHistorico) {
    let url = new URL(alvo, location.origin);
    let resposta = await requisitar(metodo, caminhoDjango(url), url.search.slice(1), corpo, tipo);
    let saltos = 0;
    while (resposta.status >= 300 && resposta.status < 400 && resposta.cabecalhos.location && saltos++ < 5) {
      url = new URL(resposta.cabecalhos.location, "http://localhost" + caminhoDjango(url));
      resposta = await requisitar("GET", url.pathname, url.search.slice(1), "", "");
    }
    const rota = url.pathname + url.search;
    rotaAtual = rota;
    if (empurrarHistorico !== false && location.hash.slice(1) !== rota) {
      history.pushState(null, "", "#" + rota);
    }
    escrever(resposta.corpo);
  }

  function escrever(html) {
    const doc = iframe.contentDocument;
    doc.open();
    doc.write(html);
    doc.close();
    document.title = doc.title || "Trilha";
    instalarInterceptadores();
  }

  function instalarInterceptadores() {
    const janela = iframe.contentWindow;
    const doc = iframe.contentDocument;

    doc.addEventListener("click", (evento) => {
      const link = evento.target.closest && evento.target.closest("a[href]");
      if (!link || evento.defaultPrevented || link.target === "_blank") return;
      const href = link.getAttribute("href");
      if (!href || href.startsWith("#") || href.startsWith("javascript:")) return;
      const url = new URL(href, "http://localhost" + (location.hash.slice(1) || "/"));
      if (url.origin !== "http://localhost" && !href.startsWith("/")) {        // link externo
        evento.preventDefault();
        window.open(href, "_blank", "noopener");
        return;
      }
      const real = new URL(url.pathname + url.search, location.origin);
      if (!ehRotaDoDjango(real)) return;
      evento.preventDefault();
      navegar("GET", url.pathname + url.search);
    });

    doc.addEventListener("submit", (evento) => {
      if (evento.defaultPrevented) return;
      const form = evento.target;
      evento.preventDefault();
      const dados = new FormData(form, evento.submitter || undefined);
      const corpo = new URLSearchParams(dados).toString();
      const acao = form.getAttribute("action") || (location.hash.slice(1) || "/");
      const metodo = (form.getAttribute("method") || "get").toUpperCase();
      if (metodo === "GET") {
        const url = new URL(acao, "http://localhost" + (location.hash.slice(1) || "/"));
        navegar("GET", url.pathname + "?" + corpo);
      } else {
        navegar("POST", acao.startsWith("/") ? acao : new URL(acao, "http://localhost" + (location.hash.slice(1) || "/")).pathname,
                corpo, "application/x-www-form-urlencoded");
      }
    });

    // fetch() da própria página (a busca no Google Books chama /trilha/buscar/).
    const fetchOriginal = janela.fetch.bind(janela);
    janela.fetch = async (entrada, opcoes) => {
      const url = new URL(typeof entrada === "string" ? entrada : entrada.url, location.origin);
      if (!ehRotaDoDjango(url)) return fetchOriginal(entrada, opcoes);
      const r = await requisitar((opcoes && opcoes.method) || "GET", caminhoDjango(url), url.search.slice(1), "", "");
      return new Response(r.corpo, { status: r.status, headers: { "content-type": r.cabecalhos["content-type"] || "text/html" } });
    };
  }

  let rotaAtual = null;
  function irParaHash() {
    const rota = location.hash.slice(1) || "/";
    if (ponte && rota !== rotaAtual) navegar("GET", rota, "", "", false);
  }
  window.addEventListener("popstate", irParaHash);
  window.addEventListener("hashchange", irParaHash);   // link colado ou hash editado à mão

  // ---------- inicialização ----------

  async function iniciar() {
    pyodide = await loadPyodide();
    etapa.textContent = "Instalando o Django";
    await pyodide.loadPackage(["micropip", "requests", "pyodide-http", "tzdata"]);
    const manifesto = await (await fetch(new URL("wheels/manifesto.json", BASE))).json();
    const micropip = pyodide.pyimport("micropip");
    await micropip.install(manifesto.map((nome) => new URL("wheels/" + nome, BASE).href), { deps: false });

    etapa.textContent = "Carregando o projeto";
    const pacote = await (await fetch(new URL("app.zip", BASE))).arrayBuffer();
    pyodide.unpackArchive(pacote, "zip", { extractDir: "/app" });
    pyodide.runPython("import sys; sys.path.insert(0, '/app')");

    etapa.textContent = "Abrindo o banco de dados deste navegador";
    FS = pyodide.FS;
    FS.mkdirTree("/dados");
    FS.mount(pyodide.FS.filesystems.IDBFS, {}, "/dados");
    await new Promise((ok, falha) => FS.syncfs(true, (erro) => (erro ? falha(erro) : ok())));

    etapa.textContent = "Preparando as tabelas";
    ponte = pyodide.pyimport("ponte");
    ponte.iniciar(STATIC_URL);
    await sincronizarBanco();

    document.getElementById("carregando").remove();
    iframe.hidden = false;
    await navegar("GET", location.hash.slice(1) || "/", "", "", false);
  }

  iniciar().catch((erro) => {
    console.error(erro);
    etapa.className = "erro";
    etapa.textContent = "Não foi possível carregar: " + erro.message;
  });
})();
