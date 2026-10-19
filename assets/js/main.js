const LINK_DASHBOARD = ""; // COLE AQUI O LINK DO SEU DASHBOARD (link publicado)

/**
 * Projeto Final — interações da página de portfólio.
 * JavaScript puro, sem bibliotecas e sem requisições de rede: todo o conteúdo
 * já está na marcação e continua visível se este arquivo não carregar.
 */
(function () {
  "use strict";

  const raiz = document.documentElement;
  raiz.classList.add("js");

  const reduzirMovimento = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const temObserver = "IntersectionObserver" in window;

  /* ---------- Link do dashboard publicado ---------- */
  // Sem link, a marcação mostra só o aviso "Dashboard em construção" (um <a> sem href, que não é clicável).
  function configurarLinkDashboard() {
    const link = document.getElementById("link-dashboard");
    const url = LINK_DASHBOARD.trim();
    if (!link || !url) return;
    const aviso = document.createElement("span");
    aviso.className = "sr-only";
    aviso.textContent = " (abre em nova aba)";
    link.href = url;
    link.className = "btn btn--primary";
    link.textContent = "Abrir dashboard publicado";
    link.appendChild(aviso);
    link.target = "_blank";
    link.rel = "noopener";
  }

  /* ---------- Menu móvel ---------- */
  function configurarMenu() {
    const botao = document.querySelector(".nav-toggle");
    const nav = document.querySelector(".site-nav");
    if (!botao || !nav) return;

    function fechar() {
      botao.setAttribute("aria-expanded", "false");
      nav.classList.remove("is-open");
    }

    botao.addEventListener("click", function () {
      const aberto = botao.getAttribute("aria-expanded") === "true";
      botao.setAttribute("aria-expanded", String(!aberto));
      nav.classList.toggle("is-open", !aberto);
    });

    nav.addEventListener("click", function (evento) {
      if (evento.target.closest("a")) fechar();
    });

    document.addEventListener("keydown", function (evento) {
      if (evento.key === "Escape" && nav.classList.contains("is-open")) {
        fechar();
        botao.focus();
      }
    });
  }

  /* ---------- Destaque da seção ativa ---------- */
  function configurarSecaoAtiva() {
    const links = Array.from(document.querySelectorAll('.nav-list a[href^="#"]'));
    const secoes = links
      .map(function (a) { return document.querySelector(a.getAttribute("href")); })
      .filter(Boolean);
    if (!temObserver || !secoes.length) return;

    const ultima = secoes[secoes.length - 1];
    let idNaFaixa = secoes[0].id; // seção que cruza a faixa central da tela
    let idMarcado = null;

    function marcar(id) {
      if (id === idMarcado) return;
      idMarcado = id;
      links.forEach(function (a) {
        if (a.getAttribute("href") === "#" + id) {
          a.setAttribute("aria-current", "true");
        } else {
          a.removeAttribute("aria-current");
        }
      });
    }

    // No fim da página, a última seção (Conclusão) pode não chegar à faixa central: ela é marcada direto.
    function atualizar() {
      const noFim = window.innerHeight + window.scrollY >= raiz.scrollHeight - 2;
      marcar(noFim ? ultima.id : idNaFaixa);
    }

    const observador = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (entrada) {
        if (entrada.isIntersecting) idNaFaixa = entrada.target.id;
      });
      atualizar();
    }, { rootMargin: "-45% 0px -50% 0px", threshold: 0 });

    secoes.forEach(function (secao) { observador.observe(secao); });
    window.addEventListener("scroll", atualizar, { passive: true });
    atualizar();
  }

  /* ---------- Contadores dos KPIs (só animam o valor já escrito na marcação) ---------- */
  function animarContador(el) {
    const alvo = parseFloat(el.dataset.valor);
    if (Number.isNaN(alvo)) return;
    const casas = parseInt(el.dataset.casas || "0", 10);
    const prefixo = el.dataset.prefixo || "";
    const sufixo = el.dataset.sufixo || "";
    const formato = new Intl.NumberFormat("pt-BR", {
      minimumFractionDigits: casas,
      maximumFractionDigits: casas
    });
    const textoFinal = el.textContent;
    const duracao = 1200;
    let inicio = null;
    let concluido = false;

    function finalizar() {
      concluido = true;
      el.textContent = textoFinal; // garante o texto exato da marcação
    }

    function passo(agora) {
      if (concluido) return;
      if (inicio === null) inicio = agora;
      const t = Math.min((agora - inicio) / duracao, 1);
      const suave = 1 - Math.pow(1 - t, 3);
      el.textContent = prefixo + formato.format(alvo * suave) + sufixo;
      if (t < 1) {
        window.requestAnimationFrame(passo);
      } else {
        finalizar();
      }
    }
    window.requestAnimationFrame(passo);
    // Rede de segurança: se os quadros forem pausados (aba em segundo plano), o valor final aparece mesmo assim.
    window.setTimeout(finalizar, duracao + 150);
  }

  /* ---------- Revelação ao rolar + contadores ---------- */
  function configurarRevelacao() {
    const elementos = Array.from(document.querySelectorAll(".reveal"));
    const contadores = Array.from(document.querySelectorAll(".kpi[data-valor]"));
    if (reduzirMovimento || !temObserver) return; // conteúdo fica visível e estático

    // Só esconde o que ainda está fora da tela; o que já está visível não pisca.
    const alturaTela = window.innerHeight || raiz.clientHeight;
    elementos.forEach(function (el) {
      if (el.getBoundingClientRect().top > alturaTela) el.classList.add("reveal-pending");
    });

    const observador = new IntersectionObserver(function (entradas, obs) {
      entradas.forEach(function (entrada) {
        if (!entrada.isIntersecting) return;
        entrada.target.classList.add("is-visible");
        obs.unobserve(entrada.target);
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.05 });
    elementos.forEach(function (el) {
      if (el.classList.contains("reveal-pending")) observador.observe(el);
    });

    const obsContador = new IntersectionObserver(function (entradas, obs) {
      entradas.forEach(function (entrada) {
        if (!entrada.isIntersecting) return;
        animarContador(entrada.target);
        obs.unobserve(entrada.target);
      });
    }, { threshold: 0.6 });
    contadores.forEach(function (el) { obsContador.observe(el); });
  }

  /* ---------- Abas da pré-visualização do dashboard ---------- */
  function configurarAbas() {
    const lista = document.querySelector(".tabs__list");
    if (!lista) return;
    const abas = Array.from(lista.querySelectorAll('[role="tab"]'));
    const paineis = abas.map(function (aba) {
      return document.getElementById(aba.getAttribute("aria-controls"));
    });
    if (paineis.some(function (p) { return !p; })) return;

    lista.hidden = false;
    lista.closest(".tabs").classList.add("tabs--ativas");
    paineis.forEach(function (painel) {
      painel.setAttribute("role", "tabpanel");
      painel.setAttribute("tabindex", "0");
    });

    function selecionar(indice, focar) {
      abas.forEach(function (aba, i) {
        const ativa = i === indice;
        aba.setAttribute("aria-selected", String(ativa));
        aba.tabIndex = ativa ? 0 : -1;
        paineis[i].hidden = !ativa;
      });
      if (focar) abas[indice].focus();
    }

    abas.forEach(function (aba, i) {
      aba.addEventListener("click", function () { selecionar(i, false); });
      aba.addEventListener("keydown", function (evento) {
        let destino = null;
        if (evento.key === "ArrowRight") destino = (i + 1) % abas.length;
        if (evento.key === "ArrowLeft") destino = (i - 1 + abas.length) % abas.length;
        if (evento.key === "Home") destino = 0;
        if (evento.key === "End") destino = abas.length - 1;
        if (destino !== null) {
          evento.preventDefault();
          selecionar(destino, true);
        }
      });
    });

    selecionar(0, false);
  }

  /* ---------- Filtro da galeria ---------- */
  function configurarFiltros() {
    const grupo = document.querySelector(".filtros");
    if (!grupo) return;
    const botoes = Array.from(grupo.querySelectorAll("[data-filtro]"));
    const itens = Array.from(document.querySelectorAll(".galeria__item"));
    grupo.hidden = false;

    botoes.forEach(function (botao) {
      botao.addEventListener("click", function () {
        const filtro = botao.dataset.filtro;
        botoes.forEach(function (b) { b.setAttribute("aria-pressed", String(b === botao)); });
        itens.forEach(function (item) {
          const mostrar = filtro === "todos" || item.dataset.categoria === filtro;
          item.hidden = !mostrar;
          if (mostrar) item.classList.add("is-visible");
        });
      });
    });
  }

  /* ---------- Lightbox ---------- */
  function configurarLightbox() {
    const dialogo = document.getElementById("lightbox");
    if (!dialogo || typeof dialogo.showModal !== "function") return; // sem suporte: o link abre a imagem
    const imagem = dialogo.querySelector(".lightbox__img");
    const titulo = dialogo.querySelector(".lightbox__titulo");
    const links = Array.from(document.querySelectorAll(".galeria__link"));
    let atual = 0;
    let origem = null;

    function visiveis() {
      return links.filter(function (a) { return !a.closest(".galeria__item").hidden; });
    }

    function mostrar(link) {
      const miniatura = link.querySelector("img");
      atual = links.indexOf(link);
      imagem.src = link.getAttribute("href");
      imagem.alt = miniatura ? miniatura.alt : "";
      titulo.textContent = link.querySelector(".galeria__cap").textContent.trim();
    }

    function navegar(passo) {
      const lista = visiveis();
      if (!lista.length) return;
      let pos = lista.indexOf(links[atual]);
      pos = (pos + passo + lista.length) % lista.length;
      mostrar(lista[pos]);
    }

    links.forEach(function (link) {
      link.addEventListener("click", function (evento) {
        evento.preventDefault();
        origem = link;
        mostrar(link);
        dialogo.showModal();
        dialogo.querySelector('[data-acao="fechar"]').focus();
      });
    });

    dialogo.addEventListener("click", function (evento) {
      const acao = evento.target.closest("[data-acao]");
      if (acao) {
        if (acao.dataset.acao === "fechar") dialogo.close();
        if (acao.dataset.acao === "anterior") navegar(-1);
        if (acao.dataset.acao === "proximo") navegar(1);
        return;
      }
      if (evento.target === dialogo) dialogo.close(); // clique no fundo
    });

    dialogo.addEventListener("keydown", function (evento) {
      if (evento.key === "ArrowRight") navegar(1);
      if (evento.key === "ArrowLeft") navegar(-1);
      if (evento.key === "Tab") {
        // Mantém o foco preso dentro do diálogo.
        const focaveis = Array.from(dialogo.querySelectorAll("button"));
        const primeiro = focaveis[0];
        const ultimo = focaveis[focaveis.length - 1];
        if (evento.shiftKey && document.activeElement === primeiro) {
          evento.preventDefault();
          ultimo.focus();
        } else if (!evento.shiftKey && document.activeElement === ultimo) {
          evento.preventDefault();
          primeiro.focus();
        }
      }
    });

    // Esc fecha nativamente; ao fechar, o foco volta para o gráfico de origem.
    dialogo.addEventListener("close", function () {
      if (origem) origem.focus();
    });
  }

  /* ---------- Ano no rodapé ---------- */
  function configurarAno() {
    const ano = document.getElementById("ano");
    if (ano) ano.textContent = String(new Date().getFullYear());
  }

  function iniciar() {
    configurarLinkDashboard();
    configurarMenu();
    configurarSecaoAtiva();
    configurarAbas();
    configurarFiltros();
    configurarLightbox();
    configurarRevelacao();
    configurarAno();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", iniciar);
  } else {
    iniciar();
  }
})();
