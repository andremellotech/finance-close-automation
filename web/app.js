"use strict";
const datasets = JSON.parse(document.getElementById("demo-data").textContent);
const reportContext = JSON.parse(document.getElementById('report-context').textContent);
let caseKey = Object.keys(datasets)[0];
let view = "overview";
let query = "";
let statusFilter = "";
let areaFilter = "";
const $ = selector => document.querySelector(selector);
const esc = value => String(value ?? "—").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const brl = value => value == null ? "—" : new Intl.NumberFormat("pt-BR", {style:"currency",currency:"BRL"}).format(value / 100);
const labels = {APROVADO:"Aprovado", PENDENTE:"Pendente", DUPLICADO:"Duplicado", CONFLITO:"Conflito de ID", CONCILIADO:"Conciliado", DIVERGENTE:"Divergente", INCOMPLETO:"Incompleto", SEM_CONTROLE:"Sem controle", ARQUIVO_AUSENTE:"Arquivo ausente", VAZIO:"Vazio"};
const errors = {CENTRO_DESCONHECIDO:"Centro de custo desconhecido", CATEGORIA_DESCONHECIDA:"Categoria desconhecida", VALOR_INVALIDO:"Valor não numérico ou diferente do formato configurado", DATA_INVALIDA:"Data inválida", DATA_FORMATO_INVALIDO:"Data diferente do formato configurado", FORA_COMPETENCIA:"Fora da competência", SINAL_INCOMPATIVEL:"Sinal incompatível com a categoria", DUPLICATA_EXATA:"Repetição exata do lançamento", CONFLITO_ID:"Mesmo ID com campos diferentes", FORMULA_NAO_ACEITA:"Fórmula na entrada Excel"};
const reason = code => code.startsWith("CAMPO_VAZIO:") ? `Campo vazio: ${code.split(":")[1]}` : errors[code] || code;
const kind = status => ["APROVADO","CONCILIADO"].includes(status) ? "ok" : status === "CONFLITO" ? "error" : status === "DUPLICADO" ? "neutral" : "warn";
const pill = status => `<span class="pill ${kind(status)}">${esc(labels[status] || status)}</span>`;
const fileName = name => `<span class="file-type">${esc(name.split(".").pop().toUpperCase())}</span><span class="file-name">${esc(name)}</span>`;
const data = () => datasets[caseKey];
const counted = (n, singular, plural) => `${n} ${n === 1 ? singular : plural}`;

function heading(title, description, counter = "") {
  return `<div class="panel-heading"><div><h2>${title}</h2><p>${description}</p></div>${counter ? `<span class="counter">${counter}</span>` : ""}</div>`;
}
function wrapTable(headers, rows, empty = "Nenhuma linha nesta seleção.") {
  return `<div class="table-wrap"><table><thead><tr>${headers.map(h => `<th scope="col">${h}</th>`).join("")}</tr></thead><tbody>${rows.length ? rows.join("") : `<tr><td class="empty" colspan="${headers.length}">${empty}</td></tr>`}</tbody></table></div>`;
}
function updateTop() {
  const d = data(), s = d.resumo;
  const formatCounts = Object.keys(d.fontes).reduce((counts,name)=>{const type=name.split('.').pop().toUpperCase();counts[type]=(counts[type]||0)+1;return counts;},{});
  const formatNote = Object.entries(formatCounts).map(([type,count])=>`${count} ${type}`).join(' + ') || 'Sem fontes registradas';
  $("#case-status").innerHTML = `<span class="pill ${d.liberado ? "ok" : "warn"}">${d.liberado ? "✓ LOTE VALIDADO" : "! REVISÃO NECESSÁRIA"}</span><p>${d.liberado ? "Os registros e controles passaram nas regras configuradas. Confira também a origem dos dados." : "Base aprovada parcial. Confira as exclusões e as divergências nos controles de origem."}</p>`;
  const phases = [["Receber",`${counted(s.arquivos,'arquivo','arquivos')} · ${formatNote}`],["Validar",`${s.aprovadas} de ${s.recebidas} aprovadas`],["Conciliar",`${d.conciliacao.filter(c=>c.status==="CONCILIADO").length} de ${counted(d.conciliacao.length,'controle correto','controles corretos')}`],["Consolidar", d.liberado ? "Base validada disponível" : "Base parcial disponível"]];
  $("#steps").innerHTML = phases.map(([title,note],i)=>`<div class="step"><span>0${i+1}</span><div><b>${title}</b><small>${esc(note)}</small></div></div>`).join("");
  const cards = [["Arquivos recebidos",s.arquivos,formatNote,""],["Linhas recebidas",s.recebidas,"Lote completo",""],["Linhas aprovadas",s.aprovadas,`${Math.round(s.aprovadas / Math.max(1,s.recebidas)*100)}% dos registros`,"good"],["Linhas excluídas",s.excluidas,s.excluidas ? "Revisar antes de liberar" : "Nenhuma pendência",s.excluidas ? "warning" : "good"]];
  $("#kpis").innerHTML = cards.map(([title,value,note,color])=>`<div class="kpi"><span>${title}</span><strong class="${color}">${value}</strong><small>${note}</small></div>`).join("");
  $("#excel-download").href = reportContext.excelPaths[caseKey];
  const execution = d.execucao;
  $('#execution-meta').innerHTML = execution ? `<summary><span>Identificação da execução</span><span class="guide-hint">Versão ${esc(execution.versao_aplicacao)} · ${esc(execution.id.slice(0,8))}</span></summary><div class="audit-body"><div class="audit-grid"><div><span class="mini-label">ID DA EXECUÇÃO</span><code>${esc(execution.id)}</code></div><div><span class="mini-label">GERADO EM UTC</span><code>${esc(execution.gerado_em_utc)}</code></div><div><span class="mini-label">AMBIENTE</span><code>Programa ${esc(execution.versao_aplicacao)} · Python ${esc(execution.versao_python)}</code></div></div><h3>Configurações efetivas · SHA-256</h3>${Object.entries(execution.configuracoes).map(([name,value])=>`<div class="hash-box"><strong>${esc(name)}</strong><code>${esc(value || 'Não informado')}</code></div>`).join('')}<p>Os hashes identificam as configurações usadas; não são assinatura ou garantia de autenticidade. Os hashes das fontes estão em Rastreabilidade.</p><a class="button" href="${esc(reportContext.manifestPaths[caseKey])}" download>↓ Baixar identificação JSON</a></div>` : '<summary>Execução sem identificação registrada</summary>';
  document.querySelectorAll("[data-case]").forEach(b=>b.setAttribute("aria-pressed",String(b.dataset.case === caseKey)));
}
function overview() {
  const d = data(), s = d.resumo;
  const files = d.conciliacao.map(c=>`<tr><td>${fileName(c.arquivo)}</td><td class="numeric">${c.linhas_recebidas}</td><td>${pill(c.status)}</td></tr>`);
  const types = [["Aprovadas",s.aprovadas,"#237a5b"],["Pendências de validação",s.pendentes,"#cf9a3c"],["Conflitos de ID",s.conflitos,"#b85f52"],["Duplicatas excluídas",s.duplicadas,"#7c9197"]];
  return `<div class="grid"><article class="panel-card">${heading("Arquivos do fechamento","As fontes recebidas e o resultado dos controles.",counted(s.arquivos,"fonte","fontes"))}${wrapTable(["Arquivo","Linhas","Conciliação"],files)}<p class="under-note">O controle compara os totais recebidos com os valores declarados na origem.</p></article><article class="panel-card">${heading("Qualidade do lote","Cada linha recebe uma classificação única.")}<div class="composition" aria-label="Distribuição das classificações">${types.map(([name,count,color])=>`<span title="${name}: ${count}" style="width:${count/Math.max(1,s.recebidas)*100}%;background:${color}"></span>`).join("")}</div>${types.map(([name,count,color])=>`<div class="issue-row"><span style="background:${color}"></span><div>${name}</div><b>${count}</b></div>`).join("")}<button type="button" class="link-button" data-open="issues">Ver as linhas para revisão →</button></article></div><div class="bridge"><div><span>Resultado da base aprovada ${d.liberado ? "· validada" : "· parcial"}</span><strong>${brl(s.total_aprovado_centavos)}</strong><small>Receitas menos gastos das linhas aprovadas</small></div><div><span>Receitas aprovadas</span><strong>${brl(s.receitas_centavos)}</strong><small>Categorias de natureza receita</small></div><div><span>Gastos líquidos aprovados</span><strong>${brl(s.gastos_centavos)}</strong><small>Gastos com sinal invertido para apresentação</small></div></div>`;
}
function controls() {
  const d = data(), s = d.resumo;
  const rows = d.conciliacao.map(c=>`<tr><td>${fileName(c.arquivo)}</td><td class="numeric">${c.linhas_recebidas} / ${c.linhas_esperadas ?? "—"}</td><td class="numeric">${brl(c.total_recebido_centavos)}${c.valores_nao_quantificaveis ? `<small>${c.valores_nao_quantificaveis} valor não quantificável</small>` : ""}</td><td class="numeric">${brl(c.total_esperado_centavos)}</td><td class="numeric">${brl(c.diferenca_centavos)}</td><td>${pill(c.status)}</td></tr>`);
  return `<article class="panel-card">${heading("Conciliação por arquivo","Quantidade e total recebidos, antes da exclusão de linhas.")} ${wrapTable(["Arquivo","Linhas: recebidas / controle","Recebido quantificável","Controle","Diferença","Status"],rows)}<div class="control-note">Com valor inválido, o total recebido mostra somente a parcela quantificável. A diferença fica sem valor e o arquivo recebe status Incompleto.</div><div class="bridge"><div><span>Recebido quantificável</span><strong>${brl(s.total_recebido_centavos)}</strong></div><div><span>Aprovado + excluído quantificável</span><strong>${brl(s.total_aprovado_centavos)}<small>+ ${brl(s.total_excluido_centavos)} excluídos</small></strong></div><div><span>Diferença da ponte</span><strong>${brl(s.total_recebido_centavos-s.total_aprovado_centavos-s.total_excluido_centavos)}</strong><small>${s.valores_nao_quantificaveis} valor(es) não quantificável(is), informado(s) separadamente</small></div></div></article>`;
}
function filteredRows() {
  const needle = query.toLocaleLowerCase("pt-BR");
  return data().linhas.filter(r=>(view !== "issues" || r.status !== "APROVADO") && (!statusFilter || r.status === statusFilter) && (!areaFilter || r.centro_custo === areaFilter) && (!needle || [r.registro_id,r.arquivo,r.descricao,...r.erros.map(reason)].join(" ").toLocaleLowerCase("pt-BR").includes(needle)));
}
function rowTable() {
  const d = data(), rows = filteredRows();
  const total = view === "issues" ? d.resumo.excluidas : d.resumo.recebidas;
  const statuses = (view === "issues" ? ["PENDENTE","CONFLITO","DUPLICADO"] : ["APROVADO","PENDENTE","CONFLITO","DUPLICADO"]);
  const areas = [...new Set(d.linhas.map(r=>r.centro_custo))].sort();
  const toolbar = `<div class="table-toolbar"><label class="field grow">Buscar ID, arquivo ou motivo<input id="search" type="search" placeholder="Ex.: ENG-001 ou competência" value="${esc(query)}"></label><label class="field">Classificação<select id="status-filter"><option value="">Todas</option>${statuses.map(s=>`<option value="${s}" ${statusFilter===s?"selected":""}>${labels[s]}</option>`).join("")}</select></label><label class="field">Centro de custo<select id="area-filter"><option value="">Todos</option>${areas.map(a=>`<option value="${esc(a)}" ${areaFilter===a?"selected":""}>${esc(a)}</option>`).join("")}</select></label><button type="button" class="button" id="export-filtered">↓ Exportar seleção CSV</button></div>`;
  const body = rows.map(r=>`<tr><td><strong>${esc(r.registro_id || "ID ausente")}</strong><small>${esc(r.centro_custo)} · ${esc(r.categoria)}</small></td><td>${esc(r.arquivo)}<small>${esc(r.aba)} · linha ${r.linha}</small></td><td>${esc(r.data_competencia)}</td><td class="numeric">${r.valor_centavos == null ? esc(r.valor_brl || "Valor ausente") : brl(r.valor_centavos)}</td><td>${pill(r.status)}</td><td class="long">${r.erros.length ? r.erros.map(reason).map(esc).join("; ") : "Regras atendidas"}${(r.orientacoes||[]).map(a=>`<small class="action"><b>Como revisar:</b> ${esc(a.acao)}</small>`).join('')}</td></tr>`);
  return `<article class="panel-card">${heading(view === "issues" ? "Linhas para revisão" : "Rastreabilidade dos lançamentos",view === "issues" ? "Corrija os arquivos de origem e execute a rotina novamente." : "Cada registro conserva arquivo, aba, linha e classificação.",`<span id="visible-count">${rows.length}</span> de ${total} linhas`)}${toolbar}<div id="rows-table">${wrapTable(["ID / classificação financeira","Origem","Competência","Valor","Status","Motivo"],body,view === "issues" && !total ? "Nenhuma pendência neste lote. Todas as linhas foram aprovadas." : undefined)}</div><p class="under-note">Os indicadores no topo continuam mostrando o lote completo. O CSV exportado respeita a seleção atual.</p>${view === "trace" ? `<div class="source-hashes">${Object.entries(d.fontes).map(([name,source])=>`<div class="hash-box"><strong>${esc(name)}</strong><code>${esc(source.sha256)}</code></div>`).join("")}</div><p class="under-note">SHA-256 dos arquivos de entrada: identifica a versão de cada fonte processada.</p>` : ""}</article>`;
}
function renderPanel() {
  $("#panel").innerHTML = view === "overview" ? overview() : view === "controls" ? controls() : rowTable();
  $("#panel").setAttribute("aria-labelledby",`tab-${view}`);
  document.querySelectorAll("[data-view]").forEach(b=>b.setAttribute("aria-selected",String(b.dataset.view===view)));
  document.querySelectorAll("[data-open]").forEach(b=>b.addEventListener("click",()=>setView(b.dataset.open)));
  if (["issues","trace"].includes(view)) {
    $("#status-filter").addEventListener("change",event=>{statusFilter=event.target.value; renderPanel();});
    $("#area-filter").addEventListener("change",event=>{areaFilter=event.target.value; renderPanel();});
    $("#search").addEventListener("input",event=>{
      query=event.target.value;
      const position=event.target.selectionStart;
      renderPanel();
      $("#search").focus();
      $("#search").setSelectionRange(position,position);
    });
    $("#export-filtered").addEventListener("click",exportFiltered);
  }
}
function setView(next) {view=next;query="";statusFilter="";areaFilter="";renderPanel();}
function exportFiltered() {
  const quote = value => {
    let text=String(value ?? "");
    if (/^[=+@-]/.test(text.trimStart()) && !/^-?\d+(\.\d+)?$/.test(text)) text="'"+text;
    return '"'+text.replace(/"/g,'""')+'"';
  };
  const cents = value => value == null ? "" : `${value < 0 ? "-" : ""}${Math.floor(Math.abs(value)/100)}.${String(Math.abs(value)%100).padStart(2,"0")}`;
  const rows=[["registro_id","arquivo","aba","linha","data_competencia","centro_custo","categoria","descricao","valor_brl","status","motivos","acao_sugerida"],...filteredRows().map(r=>[r.registro_id,r.arquivo,r.aba,r.linha,r.data_competencia,r.centro_custo,r.categoria,r.descricao,r.valor_centavos == null ? r.valor_brl : cents(r.valor_centavos),r.status,r.erros.map(reason).join(" | "),(r.orientacoes||[]).map(a=>a.acao).join(' | ')])];
  const url=URL.createObjectURL(new Blob(["\uFEFF"+rows.map(row=>row.map(quote).join(";")).join("\r\n")],{type:"text/csv;charset=utf-8"}));
  const link=document.createElement("a");link.href=url;link.download=`${view}-${caseKey}-${data().competencia}.csv`;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
document.querySelectorAll("[data-case]").forEach(b=>b.addEventListener("click",()=>{caseKey=b.dataset.case;query="";statusFilter="";areaFilter="";updateTop();renderPanel();}));
const tabs=[...document.querySelectorAll("[data-view]")];
tabs.forEach((b,i)=>{b.addEventListener("click",()=>setView(b.dataset.view));b.addEventListener("keydown",event=>{if(["ArrowLeft","ArrowRight"].includes(event.key)){event.preventDefault();const next=tabs[(i+(event.key==="ArrowRight"?1:tabs.length-1))%tabs.length];next.focus();setView(next.dataset.view);}});});
updateTop();renderPanel();
