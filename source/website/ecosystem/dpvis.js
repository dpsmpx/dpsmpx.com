/* DPvisualisation — просмотрщик (сборка). Исходники: viewer/src/. */
(function () {
"use strict";
// ---- format.js
// Форматирование для просмотрщика: даты, возраст, числа, склонения (D-10: тексты по-русски).

const MSK_OFFSET_MIN = 180; // дни и время — по московскому времени автора (rules.TZ)

function toMsk(iso) {
  if (!iso) return null;
  const t = Date.parse(iso.length === 10 ? iso + "T00:00:00+03:00" : iso);
  if (Number.isNaN(t)) return null;
  return new Date(t + MSK_OFFSET_MIN * 60000);
}

function pad(n) {
  return String(n).padStart(2, "0");
}

// «06.10.2026»; у даты без времени — то же.
function fmtDate(iso) {
  const d = toMsk(iso);
  if (!d) return "—";
  return `${pad(d.getUTCDate())}.${pad(d.getUTCMonth() + 1)}.${d.getUTCFullYear()}`;
}

// «06.10.2026 20:03»; у даты без времени — только дата.
function fmtDateTime(iso) {
  if (!iso) return "—";
  if (iso.length === 10) return fmtDate(iso);
  const d = toMsk(iso);
  if (!d) return "—";
  return `${fmtDate(iso)} ${pad(d.getUTCHours())}:${pad(d.getUTCMinutes())}`;
}

function plural(n, one, few, many) {
  const a = Math.abs(n) % 100;
  const b = a % 10;
  if (a > 10 && a < 20) return many;
  if (b > 1 && b < 5) return few;
  if (b === 1) return one;
  return many;
}

// Возраст момента относительно now: «12 мин назад», «3 ч назад», «2 дн. назад».
// Дата без времени — возраст в днях от начала дня.
function fmtAge(iso, now = Date.now()) {
  if (!iso) return "нет данных";
  const t = Date.parse(iso.length === 10 ? iso + "T00:00:00+03:00" : iso);
  if (Number.isNaN(t)) return "нет данных";
  const min = Math.max(0, Math.round((now - t) / 60000));
  if (iso.length === 10) {
    const days = Math.floor(min / 1440);
    if (days === 0) return "сегодня";
    if (days === 1) return "вчера";
    return `${days} ${plural(days, "день", "дня", "дней")} назад`;
  }
  if (min < 1) return "только что";
  if (min < 60) return `${min} мин назад`;
  const h = Math.round(min / 60);
  if (h < 48) return `${h} ч назад`;
  const days = Math.round(h / 24);
  return `${days} ${plural(days, "день", "дня", "дней")} назад`;
}

// Срез старше суток — «устарел» (F-31).
function isStale(iso, now = Date.now()) {
  const t = Date.parse(iso || "");
  return Number.isNaN(t) ? true : now - t > 24 * 3600 * 1000;
}

function fmtNum(n) {
  if (n === null || n === undefined) return "—";
  return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, " ");
}

function fmtShare(part, total) {
  if (!total) return "—";
  return `${Math.round((100 * part) / total)} %`;
}

// Дни окна: ISO-даты от start до end включительно.
function windowDays(start, days) {
  const out = [];
  const t0 = Date.parse(start + "T00:00:00Z");
  for (let i = 0; i < days; i++) {
    const d = new Date(t0 + i * 86400000);
    out.push(`${d.getUTCFullYear()}-${pad(d.getUTCMonth() + 1)}-${pad(d.getUTCDate())}`);
  }
  return out;
}

function sum(a) {
  return (a || []).reduce((x, y) => x + y, 0);
}

// ---- data.js
// Данные просмотрщика: модель (dpvis-model/1) + срез (dpvis-state/1) или публичная
// сборка (dpvis-public/1, D-15) → одно представление для экрана. Чистые функции — тесты node.


const MODEL_SCHEMA = "dpvis-model/1";
const STATE_SCHEMA = "dpvis-state/1";
const PUBLIC_SCHEMA = "dpvis-public/1";

class DataError extends Error {}

// Разобрать загруженный документ (F-37, F-38): что это — модель, срез или публичная сборка.
function classify(doc) {
  if (!doc || typeof doc !== "object" || Array.isArray(doc)) {
    throw new DataError("файл не похож на данные DPvisualisation: ждали объект JSON");
  }
  if (doc.schema === PUBLIC_SCHEMA) {
    if (!doc.model || !Array.isArray(doc.model.nodes)) throw new DataError("в публичной сборке нет модели");
    return { model: doc.model, state: doc.state || null, public: true };
  }
  if (doc.schema === MODEL_SCHEMA) {
    if (!Array.isArray(doc.nodes) || !Array.isArray(doc.flows)) throw new DataError("в модели нет узлов или потоков");
    return { model: doc };
  }
  if (doc.schema === STATE_SCHEMA) {
    if (!doc.nodes || !doc.flows) throw new DataError("в срезе нет узлов или потоков");
    return { state: doc };
  }
  throw new DataError(`неподдерживаемый формат: schema = ${JSON.stringify(doc.schema ?? null)}; ждали dpvis-model/1, dpvis-state/1 или dpvis-public/1`);
}

function index(list) {
  const out = new Map();
  for (const x of list || []) out.set(x.id, x);
  return out;
}

function zeros(n) {
  return new Array(n).fill(0);
}

function fit(arr, n) {
  if (!Array.isArray(arr)) return zeros(n);
  if (arr.length === n) return arr.slice();
  if (arr.length > n) return arr.slice(arr.length - n);
  return zeros(n - arr.length).concat(arr);
}

function lastN(arr, k) {
  return sum(arr.slice(Math.max(0, arr.length - k)));
}

// ISO момента или даты → индекс дня окна; до окна — -1, после — days.
function dayIndex(iso, days) {
  if (!iso) return -1;
  const d = iso.slice(0, 10);
  const i = days.indexOf(d);
  if (i >= 0) return i;
  return d < days[0] ? -1 : days.length;
}

// Ветки с невлитой работой: в полной модели — список, в публичной — число (D-15).
function branchInfo(git) {
  if (!git) return { count: 0, list: [], known: false };
  if (Array.isArray(git.branches)) return { count: git.branches.length, list: git.branches, known: true };
  if (typeof git.branches === "number") return { count: git.branches, list: [], known: true };
  return { count: 0, list: [], known: false }; // публичная выжимка — веток нет (D-15)
}

function normalize(model, state = null, opts = {}) {
  if (!model) throw new DataError("нет модели");
  const nDays = state?.window?.days || 30;
  const days = state?.window?.start ? windowDays(state.window.start, nDays) : windowDays(endMinus(nDays), nDays);
  const rateDays = state?.rules?.rate_days || 7;
  const cat = model.catalog || {};
  const layers = (model.layers || []).map((l, i) => ({ ...l, index: i }));
  const layerIndex = new Map(layers.map((l) => [l.id, l.index]));

  const nodes = (model.nodes || []).map((n) => {
    const st = state?.nodes?.[n.id] || null;
    const git = st?.git || null;
    const node = {
      ...n,
      layerIndex: layerIndex.has(n.layer) ? layerIndex.get(n.layer) : layers.length,
      activity: st?.activity?.state || (state ? "unknown" : "nodata"),
      last: st?.activity?.last || null,
      reasons: st?.activity?.reasons || [],
      git: null,
      daysAi: zeros(nDays),
      daysHuman: zeros(nDays),
      daysMerges: zeros(nDays),
      firstIndex: -1,
      branches: { count: 0, list: [], known: false },
      week: 0,
      windowTotal: 0,
    };
    if (git) {
      node.git = git;
      node.daysAi = fit(git.days?.ai, nDays);
      node.daysHuman = fit(git.days?.human, nDays);
      node.daysMerges = fit(git.days?.merges, nDays);
      node.firstIndex = dayIndex(git.first_time || git.first_date, days);
      node.branches = branchInfo(git);
      node.windowTotal = (git.window?.ai || 0) + (git.window?.human || 0);
    } else if (Array.isArray(st?.days)) {
      // участник: события по дням
      node.daysHuman = n.id === "author" ? fit(st.days, nDays) : zeros(nDays);
      node.daysAi = n.id === "author" ? zeros(nDays) : fit(st.days, nDays);
      node.windowTotal = sum(st.days);
    }
    node.daysTotal = node.daysAi.map((v, i) => v + node.daysHuman[i]);
    node.week = lastN(node.daysTotal, rateDays);
    return node;
  });
  const nodeById = index(nodes);

  const flows = [];
  for (const f of model.flows || []) {
    if (!nodeById.has(f.from) || !nodeById.has(f.to)) continue;
    const st = state?.flows?.[f.id] || null;
    const fdays = fit(st?.days, nDays);
    flows.push({
      ...f,
      state: st?.state || (state ? "unknown" : f.status === "active" ? "nodata" : f.status),
      days: fdays,
      week: st?.week ?? lastN(fdays, rateDays),
      total: st?.total ?? sum(fdays),
      lastEvent: st?.last || null,
    });
  }
  const flowById = index(flows);
  const outgoing = new Map(nodes.map((n) => [n.id, []]));
  const incoming = new Map(nodes.map((n) => [n.id, []]));
  for (const f of flows) {
    outgoing.get(f.from).push(f);
    incoming.get(f.to).push(f);
  }

  return {
    title: model.title || "Экосистема",
    modelAsOf: model.as_of || null,
    asOf: state?.as_of || null,
    hasState: !!state,
    public: !!opts.public,
    days,
    rateDays,
    rules: state?.rules || null,
    layers,
    catalog: {
      nodeKinds: index(cat.node_kinds),
      flowKinds: index(cat.flow_kinds),
      drivers: index(cat.drivers),
      statuses: index(cat.statuses),
      transports: index(cat.transports),
      visibility: index(cat.visibility),
      groups: index(cat.groups),
    },
    catalogLists: cat,
    nodes,
    flows,
    nodeById,
    flowById,
    outgoing,
    incoming,
    hasBranches: nodes.some((n) => n.branches.known),
    diagnostics: state?.diagnostics || null,
    registry: state?.registry || null,
    hidden: model.hidden || null,
  };
}

function endMinus(n) {
  const d = new Date(Date.now() - (n - 1) * 86400000);
  return d.toISOString().slice(0, 10);
}

// Состояние потока в выбранный день шкалы времени (F-28): событие в этот день — «идёт».
function flowStateAt(flow, dayIdx) {
  if (dayIdx === null || dayIdx === undefined) return flow.state;
  if (["planned", "blocked", "off"].includes(flow.state)) return flow.state;
  if (flow.state === "unobserved" || flow.state === "unknown" || flow.state === "nodata") return flow.state;
  return flow.days[dayIdx] > 0 ? "flowing" : "quiet";
}

function flowRateAt(flow, dayIdx, rateDays = 7) {
  if (dayIdx === null || dayIdx === undefined) return flow.week;
  return flow.days[dayIdx] * rateDays; // день в масштабе недели — та же шкала толщины линии
}

function nodeActivityAt(node, dayIdx) {
  if (dayIdx === null || dayIdx === undefined) return node.activity;
  if (node.kind === "repo" || node.kind === "actor") {
    if (!node.git && node.kind === "repo") return node.activity;
    return node.daysTotal[dayIdx] > 0 ? "working" : "idle";
  }
  return node.activity;
}

// Узел существует в выбранный день: у репозитория первый коммит не позже дня (F-28).
function nodeExistsAt(node, dayIdx) {
  if (dayIdx === null || dayIdx === undefined) return true;
  if (node.kind !== "repo" || !node.git) return true;
  return node.firstIndex <= dayIdx;
}

// ---- filters.js
// Фильтры, выбор и адрес вида (F-26, F-27, F-28): состояние ↔ строка «#…». Чистые функции.


const FLOW_STATES = ["flowing", "quiet", "planned", "blocked", "off", "unknown", "unobserved"];

const STATE_NAMES = {
  flowing: "идёт",
  quiet: "тихо",
  planned: "план",
  blocked: "заблокирован",
  off: "выключен",
  unknown: "неизвестно",
  unobserved: "не наблюдается",
  nodata: "нет данных",
  working: "работает",
  idle: "без работы",
  up: "отвечает",
  down: "не отвечает",
};

function defaults() {
  return { sel: null, kinds: null, states: null, layers: null, q: "", a7: false, day: null, tab: "graph", show: false };
}

function setParam(list) {
  return list ? [...list].sort().join(",") : null;
}

function encode(f) {
  const p = [];
  if (f.sel) p.push(["sel", f.sel]);
  if (f.kinds) p.push(["fk", setParam(f.kinds)]);
  if (f.states) p.push(["st", setParam(f.states)]);
  if (f.layers) p.push(["ly", setParam(f.layers)]);
  if (f.q) p.push(["q", f.q]);
  if (f.a7) p.push(["a7", "1"]);
  if (f.day !== null && f.day !== undefined) p.push(["day", String(f.day)]);
  if (f.tab && f.tab !== "graph") p.push(["tab", f.tab]);
  if (f.show) p.push(["show", "1"]);
  return p.length ? "#" + p.map(([k, v]) => `${k}=${encodeURIComponent(v)}`).join("&") : "";
}

function decode(hash, view = null) {
  const f = defaults();
  const s = (hash || "").replace(/^#/, "");
  if (!s) return f;
  for (const part of s.split("&")) {
    const i = part.indexOf("=");
    if (i < 0) continue;
    const k = part.slice(0, i);
    let v;
    try {
      v = decodeURIComponent(part.slice(i + 1));
    } catch {
      continue;
    }
    const list = () => new Set(v.split(",").filter(Boolean));
    if (k === "sel" && /^[nf]:[\w.\-]+$/.test(v)) f.sel = v;
    else if (k === "fk") f.kinds = list();
    else if (k === "st") f.states = list();
    else if (k === "ly") f.layers = list();
    else if (k === "q") f.q = v.slice(0, 80);
    else if (k === "a7") f.a7 = v === "1";
    else if (k === "day" && /^\d+$/.test(v)) f.day = Number(v);
    else if (k === "tab" && ["graph", "tables", "recon"].includes(v)) f.tab = v;
    else if (k === "show") f.show = v === "1";
  }
  if (view) {
    if (f.day !== null && f.day >= view.days.length) f.day = null;
    if (f.sel) {
      const [t, id] = [f.sel[0], f.sel.slice(2)];
      if ((t === "n" && !view.nodeById.has(id)) || (t === "f" && !view.flowById.has(id))) f.sel = null;
    }
  }
  return f;
}

function matches(node, q) {
  if (!q) return true;
  const s = q.trim().toLowerCase();
  return node.name.toLowerCase().includes(s) || node.id.toLowerCase().includes(s);
}

// Что видно при фильтрах: {nodes: Set id, flows: Set id}. Поиск не скрывает, а приглушает (dimmed).
function visible(view, f) {
  const nodes = new Set();
  for (const n of view.nodes) {
    if (f.layers && !f.layers.has(n.layer)) continue;
    if (!nodeExistsAt(n, f.day)) continue;
    nodes.add(n.id);
  }
  const flows = new Set();
  for (const fl of view.flows) {
    if (!nodes.has(fl.from) || !nodes.has(fl.to)) continue;
    if (f.kinds && !f.kinds.has(fl.kind)) continue;
    const st = flowStateAt(fl, f.day);
    if (f.states && !f.states.has(st)) continue;
    if (f.a7) {
      const active = f.day === null || f.day === undefined ? fl.week > 0 : fl.days[f.day] > 0;
      if (!active) continue;
    }
    flows.add(fl.id);
  }
  if (f.a7) {
    // «только с активностью»: узлы без работы и без видимых потоков — убрать
    for (const id of [...nodes]) {
      const n = view.nodeById.get(id);
      const own = f.day === null || f.day === undefined ? n.week > 0 : n.daysTotal[f.day] > 0;
      const linked = [...view.outgoing.get(id), ...view.incoming.get(id)].some((x) => flows.has(x.id));
      if (!own && !linked) nodes.delete(id);
    }
  }
  return { nodes, flows };
}

// Фокус выбора (F-26): выбранный и его соседи; для потока — он и его концы.
function focusSet(view, sel) {
  if (!sel) return null;
  const id = sel.slice(2);
  const nodes = new Set();
  const flows = new Set();
  if (sel[0] === "n") {
    nodes.add(id);
    for (const f of [...(view.outgoing.get(id) || []), ...(view.incoming.get(id) || [])]) {
      flows.add(f.id);
      nodes.add(f.from);
      nodes.add(f.to);
    }
  } else {
    const f = view.flowById.get(id);
    if (f) {
      flows.add(f.id);
      nodes.add(f.from);
      nodes.add(f.to);
    }
  }
  return { nodes, flows };
}

// ---- layout.js
// Раскладка схемы (D-16): от ширины контейнера, единица схемы — пиксель экрана, поэтому
// текст не мельчает и прокрутки вбок нет. Широко — слои колонками слева направо; узко —
// слои полосами сверху вниз, узлы в полосе — сеткой по ширине. Связь — прямой отрезок от
// края узла до края узла; несколько связей одной пары идут рядом, а не друг по другу.
// Раскладка не зависит от фильтров: при фильтрации узлы не прыгают.

const GEOM = { minNodeW: 136, maxNodeW: 190, nodeH: 44, gapX: 16, gapY: 16, headerH: 28, pad: 12, bandGap: 14, minWidth: 240 };

const GROUP_ORDER = { control: 0, core: 1, sync: 2, support: 3, new: 4, periphery: 5 };

function degree(view, id) {
  return (view.outgoing.get(id) || []).length + (view.incoming.get(id) || []).length;
}

function groupsByLayer(view) {
  const cols = view.layers
    .map((l) => ({ layer: l, nodes: view.nodes.filter((n) => n.layer === l.id) }))
    .filter((c) => c.nodes.length > 0);
  const stray = view.nodes.filter((n) => !view.layers.some((l) => l.id === n.layer));
  if (stray.length) cols.push({ layer: { id: "other", name: "Прочее" }, nodes: stray });
  for (const c of cols) {
    c.nodes.sort(
      (a, b) =>
        (GROUP_ORDER[a.group] ?? 4) - (GROUP_ORDER[b.group] ?? 4) ||
        degree(view, b.id) - degree(view, a.id) ||
        a.name.localeCompare(b.name, "ru"),
    );
  }
  return cols;
}

// Подпись слоя в колонку: длинная — в две строки по пробелу у середины. Ширина
// знака — с запасом под прописные 12 px с разрядкой (style.css, .col-name).
function splitHeader(name, width) {
  const max = Math.max(6, Math.floor((width - 10) / 8.4));
  if (name.length <= max || !name.includes(" ")) return [name];
  const mid = name.length / 2;
  let best = -1;
  for (let i = 0; i < name.length; i++) if (name[i] === " " && (best < 0 || Math.abs(i - mid) < Math.abs(best - mid))) best = i;
  return [name.slice(0, best), name.slice(best + 1)];
}

function neighbours(view, id) {
  return [...(view.outgoing.get(id) || []), ...(view.incoming.get(id) || [])].map((f) => (f.from === id ? f.to : f.from));
}

// Колонки: порядок в колонке — по среднему положению соседей в других колонках
// (меньше пересечений), несколько проходов туда и обратно.
function columns(view, cols, W, g) {
  const colW = (W - 2 * g.pad) / cols.length;
  const nodeW = Math.min(g.maxNodeW, Math.floor(colW - g.gapX));
  const colOf = new Map();
  cols.forEach((c, i) => c.nodes.forEach((n) => colOf.set(n.id, i)));
  const maxRows = Math.max(...cols.map((c) => c.nodes.length));
  const fullH = maxRows * (g.nodeH + g.gapY) - g.gapY;
  const lines = cols.map((c) => splitHeader(c.layer.name, colW));
  const top0 = g.pad + g.headerH + (lines.some((l) => l.length > 1) ? 14 : 0);
  const yOf = new Map();
  const place = () => {
    for (const c of cols) {
      const h = c.nodes.length * (g.nodeH + g.gapY) - g.gapY;
      const top = top0 + (fullH - h) / 2;
      c.nodes.forEach((n, i) => yOf.set(n.id, top + i * (g.nodeH + g.gapY)));
    }
  };
  place();
  for (let pass = 0; pass < 6; pass++) {
    for (const c of pass % 2 ? [...cols].reverse() : cols) {
      const bc = new Map();
      for (const n of c.nodes) {
        const nb = neighbours(view, n.id).filter((id) => colOf.has(id) && colOf.get(id) !== colOf.get(n.id));
        bc.set(n.id, nb.length ? nb.reduce((s, id) => s + yOf.get(id), 0) / nb.length : yOf.get(n.id));
      }
      c.nodes.sort((a, b) => bc.get(a.id) - bc.get(b.id) || a.name.localeCompare(b.name, "ru"));
    }
    place();
  }
  const nodes = new Map();
  const headers = cols.map((c, i) => {
    const cx = g.pad + i * colW + colW / 2;
    for (const n of c.nodes) nodes.set(n.id, { x: Math.round(cx - nodeW / 2), y: Math.round(yOf.get(n.id)), w: nodeW, h: g.nodeH, band: i });
    return { id: c.layer.id, name: c.layer.name, lines: lines[i], x: Math.round(cx), y: g.pad + 12, anchor: "middle", w: colW };
  });
  return { nodes, headers, height: top0 + fullH + g.pad, nodeW };
}

// Полосы: слой — заголовок и сетка узлов по ширине; число узлов в ряду — сколько влезает.
function bands(view, cols, W, g) {
  const inner = W - 2 * g.pad;
  const perRow = Math.max(1, Math.floor((inner + g.gapX) / (g.minNodeW + g.gapX)));
  const nodeW = Math.min(g.maxNodeW * 1.4, Math.floor((inner - (perRow - 1) * g.gapX) / perRow));
  const nodes = new Map();
  const headers = [];
  let y = g.pad;
  cols.forEach((c, i) => {
    headers.push({ id: c.layer.id, name: c.layer.name, lines: [c.layer.name], x: g.pad, y: y + 12, anchor: "start", w: inner });
    y += g.headerH;
    c.nodes.forEach((n, j) => {
      const row = Math.floor(j / perRow);
      const col = j % perRow;
      nodes.set(n.id, { x: g.pad + col * (nodeW + g.gapX), y: y + row * (g.nodeH + g.gapY), w: nodeW, h: g.nodeH, band: i });
    });
    const rows = Math.ceil(c.nodes.length / perRow);
    y += rows * (g.nodeH + g.gapY) - g.gapY + g.bandGap;
  });
  return { nodes, headers, height: y - g.bandGap + g.pad, nodeW };
}

// Точка на краю прямоугольника по направлению от его центра (с зазором под стрелку).
function edgePoint(box, dx, dy, gap = 3) {
  const cx = box.x + box.w / 2;
  const cy = box.y + box.h / 2;
  if (dx === 0 && dy === 0) return { x: cx, y: cy };
  const tx = dx === 0 ? Infinity : (box.w / 2 + gap) / Math.abs(dx);
  const ty = dy === 0 ? Infinity : (box.h / 2 + gap) / Math.abs(dy);
  const t = Math.min(tx, ty);
  return { x: cx + dx * t, y: cy + dy * t };
}

function r(v) {
  return Math.round(v * 10) / 10;
}

function layout(view, width, g = GEOM) {
  const W = Math.max(g.minWidth, Math.floor(width || 0));
  const cols = groupsByLayer(view);
  const colW = (W - 2 * g.pad) / Math.max(1, cols.length);
  const mode = cols.length && colW >= g.minNodeW + g.gapX ? "columns" : "bands";
  const placed = cols.length ? (mode === "columns" ? columns(view, cols, W, g) : bands(view, cols, W, g)) : { nodes: new Map(), headers: [], height: 2 * g.pad, nodeW: g.minNodeW };

  // пары узлов: связи одной пары (в любую сторону) — параллельно, с шагом 5 px
  const pairs = new Map();
  for (const f of view.flows) {
    if (!placed.nodes.has(f.from) || !placed.nodes.has(f.to)) continue;
    const key = f.from < f.to ? `${f.from}|${f.to}` : `${f.to}|${f.from}`;
    if (!pairs.has(key)) pairs.set(key, []);
    pairs.get(key).push(f);
  }
  const flows = new Map();
  for (const list of pairs.values()) {
    list.sort((a, b) => (a.id < b.id ? -1 : 1));
    list.forEach((f, i) => {
      const a = placed.nodes.get(f.from);
      const b = placed.nodes.get(f.to);
      const ax = a.x + a.w / 2;
      const ay = a.y + a.h / 2;
      const dx = b.x + b.w / 2 - ax;
      const dy = b.y + b.h / 2 - ay;
      const len = Math.hypot(dx, dy) || 1;
      // смещение поперёк линии — одно и то же для пары, как бы ни была направлена связь
      const sign = f.from < f.to ? 1 : -1;
      const off = (i - (list.length - 1) / 2) * 5 * sign;
      const ox = (-dy / len) * off;
      const oy = (dx / len) * off;
      const p1 = edgePoint(a, dx, dy);
      const p2 = edgePoint(b, -dx, -dy);
      const x1 = p1.x + ox;
      const y1 = p1.y + oy;
      const x2 = p2.x + ox;
      const y2 = p2.y + oy;
      flows.set(f.id, { d: `M${r(x1)},${r(y1)} L${r(x2)},${r(y2)}`, x1, y1, x2, y2 });
    });
  }
  return { width: W, height: Math.ceil(placed.height), mode, nodes: placed.nodes, flows, headers: placed.headers, nodeW: placed.nodeW, geom: g };
}

// ---- dom.js
// Мелкие помощники DOM: только textContent и атрибуты — без innerHTML и без встроенных стилей (CSP).

function h(tag, attrs = {}, ...children) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v === null || v === undefined || v === false) continue;
    if (k === "on") {
      for (const [ev, fn] of Object.entries(v)) e.addEventListener(ev, fn);
    } else if (k === "text") {
      e.textContent = v;
    } else {
      e.setAttribute(k, v === true ? "" : String(v));
    }
  }
  for (const c of children.flat()) {
    if (c === null || c === undefined || c === false) continue;
    e.appendChild(typeof c === "string" || typeof c === "number" ? document.createTextNode(String(c)) : c);
  }
  return e;
}

function svgEl(tag, attrs = {}, parent = null) {
  const e = document.createElementNS("http://www.w3.org/2000/svg", tag);
  for (const [k, v] of Object.entries(attrs)) if (v !== null && v !== undefined) e.setAttribute(k, String(v));
  if (parent) parent.appendChild(e);
  return e;
}

// ---- graph.js
// Схема в SVG (F-21, F-23, F-26, F-33; D-16): узлы, связи — прямые со стрелкой, без анимаций.
// Интенсивность связи — толщина линии (события за неделю); масштаб — кнопками, сдвиг —
// перетаскиванием, только когда схема увеличена; иначе страница прокручивается как обычно.
// Ширина схемы — ширина контейнера: при её смене раскладка строится заново.
// Без встроенных стилей и обработчиков в разметке — работает под строгой CSP (D-05, D-15).


const NS = "http://www.w3.org/2000/svg";
let instance = 0;

function el(tag, attrs = {}, parent = null) {
  const e = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) if (v !== null && v !== undefined) e.setAttribute(k, String(v));
  if (parent) parent.appendChild(e);
  return e;
}

// Подпись узла по ширине: примерно 7,6 px на знак при 13,5 px полужирным.
function short(name, width) {
  const max = Math.max(6, Math.floor((width - 30) / 7.6));
  return name.length > max ? name.slice(0, max - 1) + "…" : name;
}

// Толщина линии — интенсивность за неделю (вместо движения частиц, D-16).
function strokeFor(state, rate) {
  if (state !== "flowing" && state !== "quiet") return 1.2;
  return Math.min(3.2, 1.2 + 0.5 * Math.log2(1 + rate));
}

const ZOOM = { min: 1, max: 4, step: 1.4 };

function createGraph(host, view, handlers) {
  const id = `dpv${++instance}`;
  let lay = null;
  let svg = null;
  let flowEls = new Map();
  let nodeEls = new Map();
  let current = null;
  let vb = null; // null — вся схема
  let moved = false;

  function draw(width, keepVb = false) {
    const prevVb = keepVb ? vb : null;
    lay = layout(view, width);
    const old = svg;
    svg = el("svg", {
      class: "dpvis-svg",
      "data-mode": lay.mode,
      viewBox: `0 0 ${lay.width} ${lay.height}`,
      width: lay.width,
      height: lay.height,
      role: "group",
      "aria-label": "Схема: проекты по слоям, связи — линии со стрелкой",
    });
    const defs = el("defs", {}, svg);
    for (const drv of ["human", "ai", "check", "data"]) {
      // стрелка — одного размера при любой толщине линии
      const m = el("marker", { id: `${id}-mk-${drv}`, viewBox: "0 0 10 10", refX: 9, refY: 5, markerWidth: 8, markerHeight: 8, orient: "auto-start-reverse", markerUnits: "userSpaceOnUse" }, defs);
      el("path", { d: "M0,1 L9,5 L0,9 z", class: `mk drv-${drv}` }, m);
    }
    const bg = el("rect", { class: "dpvis-bg", x: 0, y: 0, width: lay.width, height: lay.height }, svg);
    bg.addEventListener("click", () => {
      if (!moved) handlers.select(null);
    });
    const gFlows = el("g", { class: "flows" }, svg);
    const gHead = el("g", { class: "cols", "aria-hidden": "true" }, svg);
    for (const c of lay.headers) {
      const t = el("text", { x: c.x, y: c.y, class: "col-name", "text-anchor": c.anchor }, gHead);
      c.lines.forEach((line, i) => {
        el("tspan", { x: c.x, dy: i ? 14 : 0 }, t).textContent = line;
      });
    }
    const gNodes = el("g", { class: "nodes" }, svg);

    flowEls = new Map();
    for (const f of view.flows) {
      const geo = lay.flows.get(f.id);
      if (!geo) continue;
      const g = el("g", { class: "flow", "data-id": f.id }, gFlows);
      const path = el("path", {
        d: geo.d,
        class: `flow-line drv-${f.driver}`,
        "marker-end": `url(#${id}-mk-${f.driver})`,
        "marker-start": f.bidirectional ? `url(#${id}-mk-${f.driver})` : null,
      }, g);
      const hit = el("path", { d: geo.d, class: "flow-hit" }, g);
      const from = view.nodeById.get(f.from).name;
      const to = view.nodeById.get(f.to).name;
      el("title", {}, hit).textContent = `${from} → ${to}: ${view.catalog.flowKinds.get(f.kind)?.name || f.kind}`;
      hit.addEventListener("click", (e) => {
        e.stopPropagation();
        if (!moved) handlers.select(`f:${f.id}`);
      });
      hit.addEventListener("pointerenter", (e) => handlers.hover({ type: "flow", item: f }, e));
      hit.addEventListener("pointermove", (e) => handlers.hover({ type: "flow", item: f }, e));
      hit.addEventListener("pointerleave", () => handlers.hover(null));
      flowEls.set(f.id, { g, path });
    }

    nodeEls = new Map();
    for (const n of view.nodes) {
      const p = lay.nodes.get(n.id);
      if (!p) continue;
      const g = el("g", { class: `node kind-${n.kind}`, transform: `translate(${p.x},${p.y})`, tabindex: 0, role: "button", "data-id": n.id }, gNodes);
      el("rect", { class: "node-ring", x: -3, y: -3, width: p.w + 6, height: p.h + 6, rx: 9 }, g);
      el("rect", { class: "node-box", width: p.w, height: p.h, rx: 7 }, g);
      el("text", { class: "node-name", x: 9, y: 18 }, g).textContent = short(n.name, p.w);
      const sub = el("text", { class: "node-sub", x: 9, y: 34 }, g);
      const badge = el("g", { class: "badge", transform: `translate(${p.w - 2},2)` }, g);
      el("circle", { r: 9 }, badge);
      const bt = el("text", { "text-anchor": "middle", y: 4 }, badge);
      const q = el("text", { class: "unknown-mark", x: p.w - 13, y: 30, "text-anchor": "middle" }, g);
      q.textContent = "?";
      const title = el("title", {}, g);
      g.addEventListener("click", (e) => {
        e.stopPropagation();
        if (!moved) handlers.select(`n:${n.id}`);
      });
      g.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          handlers.select(`n:${n.id}`);
        }
      });
      g.addEventListener("pointerenter", (e) => handlers.hover({ type: "node", item: n }, e));
      g.addEventListener("pointermove", (e) => handlers.hover({ type: "node", item: n }, e));
      g.addEventListener("pointerleave", () => handlers.hover(null));
      nodeEls.set(n.id, { g, sub, badge, bt, title });
    }
    attachPan(svg);
    if (old) old.replaceWith(svg);
    else host.appendChild(svg);
    vb = prevVb && prevVb.w <= lay.width && prevVb.h <= lay.height ? clamp(prevVb) : null;
    applyVb();
    if (current) paint();
  }

  // Новые данные той же ширины: раскладка та же, масштаб и сдвиг сохраняются (F-45).
  function setView(v) {
    view = v;
    draw(lastW, true);
  }

  // ------------------------------------------------------------ состояние (F-23, F-26)
  function update(vis, focus, dimSet, day) {
    current = { vis, focus, dim: dimSet, day };
    paint();
  }

  function paint() {
    const { vis, focus, dim, day } = current;
    for (const n of view.nodes) {
      const e = nodeEls.get(n.id);
      if (!e) continue;
      const act = nodeActivityAt(n, day);
      const shown = vis.nodes.has(n.id);
      const faded = (focus && !focus.nodes.has(n.id)) || (dim && !dim.has(n.id));
      const sel = handlers.selected() === `n:${n.id}`;
      e.g.setAttribute("class", `node kind-${n.kind} act-${act} st-${n.status}${shown ? "" : " is-hidden"}${faded ? " is-dim" : ""}${sel ? " is-sel" : ""}`);
      const kindName = view.catalog.nodeKinds.get(n.kind)?.name || n.kind;
      const actName = STATE_NAMES[act] || act;
      e.sub.textContent = n.kind === "repo" || n.kind === "actor" || act === "up" || act === "down" ? actName : n.status === "active" ? kindName : view.catalog.statuses.get(n.status)?.name || n.status;
      const br = n.branches.count;
      e.badge.setAttribute("class", `badge${br > 0 && n.branches.known && day === null ? "" : " is-hidden"}`);
      e.bt.textContent = br > 9 ? "9+" : String(br);
      const parts = [n.name, kindName, actName];
      if (br > 0) parts.push(`веток с невлитой работой: ${br}`);
      e.g.setAttribute("aria-label", parts.join(", "));
      e.title.textContent = parts.join(" · ");
      e.g.setAttribute("tabindex", shown ? "0" : "-1");
    }
    for (const f of view.flows) {
      const e = flowEls.get(f.id);
      if (!e) continue;
      const st = flowStateAt(f, day);
      const rate = flowRateAt(f, day, view.rateDays);
      const shown = vis.flows.has(f.id);
      const faded = (focus && !focus.flows.has(f.id)) || (dim && !(dim.has(f.from) && dim.has(f.to)));
      const inFocus = focus && focus.flows.has(f.id);
      e.g.setAttribute("class", `flow st-${st}${shown ? "" : " is-hidden"}${faded ? " is-dim" : ""}${inFocus ? " is-focus" : ""}${handlers.selected() === `f:${f.id}` ? " is-sel" : ""}`);
      e.path.setAttribute("stroke-width", strokeFor(st, rate).toFixed(2));
    }
  }

  // ------------------------------------------------------------ масштаб и сдвиг (F-33)
  function zoomLevel() {
    return vb ? lay.width / vb.w : 1;
  }

  function applyVb() {
    const v = vb || { x: 0, y: 0, w: lay.width, h: lay.height };
    svg.setAttribute("viewBox", `${v.x} ${v.y} ${v.w} ${v.h}`);
    host.classList.toggle("is-zoomed", !!vb);
    handlers.zoomChanged?.(zoomLevel());
  }

  function clamp(v) {
    const x = Math.min(Math.max(0, v.x), lay.width - v.w);
    const y = Math.min(Math.max(0, v.y), lay.height - v.h);
    return { ...v, x, y };
  }

  function zoomTo(k, cx, cy) {
    const z = Math.min(ZOOM.max, Math.max(ZOOM.min, k));
    if (z <= ZOOM.min + 1e-6) {
      vb = null;
    } else {
      const w = lay.width / z;
      const h = lay.height / z;
      vb = clamp({ x: cx - w / 2, y: cy - h / 2, w, h });
    }
    applyVb();
  }

  function center() {
    const v = vb || { x: 0, y: 0, w: lay.width, h: lay.height };
    return { x: v.x + v.w / 2, y: v.y + v.h / 2 };
  }

  function zoomBy(k) {
    const c = center();
    zoomTo(zoomLevel() * k, c.x, c.y);
  }

  function fit() {
    vb = null;
    applyVb();
  }

  function centerOn(nid) {
    const p = lay.nodes.get(nid);
    if (!p) return;
    if (vb) {
      vb = clamp({ ...vb, x: p.x + p.w / 2 - vb.w / 2, y: p.y + p.h / 2 - vb.h / 2 });
      applyVb();
    } else {
      nodeEls.get(nid)?.g.scrollIntoView?.({ block: "center", behavior: "auto" });
    }
  }

  function toSvg(clientX, clientY) {
    const m = svg.getScreenCTM();
    if (!m) return { x: 0, y: 0 };
    const pt = svg.createSVGPoint();
    pt.x = clientX;
    pt.y = clientY;
    return pt.matrixTransform(m.inverse());
  }

  function attachPan(s) {
    // колесо масштабирует только с Ctrl или ⌘ — иначе прокручивает страницу
    s.addEventListener("wheel", (e) => {
      if (!(e.ctrlKey || e.metaKey)) return;
      e.preventDefault();
      const pt = toSvg(e.clientX, e.clientY);
      zoomTo(zoomLevel() * Math.exp(-e.deltaY * 0.0015), pt.x, pt.y);
    }, { passive: false });
    let start = null;
    s.addEventListener("pointerdown", (e) => {
      moved = false;
      start = vb ? { x: e.clientX, y: e.clientY, vb: { ...vb }, id: e.pointerId } : null;
    });
    s.addEventListener("pointermove", (e) => {
      if (!start || e.pointerId !== start.id) return;
      const dx = e.clientX - start.x;
      const dy = e.clientY - start.y;
      if (!moved && Math.hypot(dx, dy) < 5) return;
      if (!moved) s.setPointerCapture?.(e.pointerId);
      moved = true;
      const m = s.getScreenCTM();
      const scale = m ? m.a : 1;
      vb = clamp({ ...start.vb, x: start.vb.x - dx / scale, y: start.vb.y - dy / scale });
      applyVb();
      handlers.hover(null);
    });
    const end = () => {
      start = null;
      setTimeout(() => (moved = false), 0);
    };
    s.addEventListener("pointerup", end);
    s.addEventListener("pointercancel", end);
  }

  // ------------------------------------------------------------ ширина
  let lastW = 0;
  let pending = 0;
  const widthNow = () => Math.floor(host.clientWidth || 0);
  const onResize = () => {
    if (pending) return;
    pending = setTimeout(() => {
      pending = 0;
      const w = widthNow();
      if (w && Math.abs(w - lastW) > 1) {
        lastW = w;
        draw(w);
      }
    }, 60);
  };
  lastW = widthNow() || 960;
  draw(lastW);
  const ro = "ResizeObserver" in window ? new ResizeObserver(onResize) : null;
  ro?.observe(host);
  if (!ro) window.addEventListener("resize", onResize);

  function destroy() {
    ro?.disconnect();
    window.removeEventListener("resize", onResize);
    clearTimeout(pending);
    svg.remove();
  }

  return {
    get svg() { return svg; },
    get layout() { return lay; },
    update, setView, fit, zoomBy, zoomLevel, centerOn, destroy,
    nodeEls: () => nodeEls,
  };
}

// ---- panel.js
// Панель подробностей (F-24, F-25): узел или поток; у каждого графика — таблица значений.


function row(label, value) {
  if (value === null || value === undefined || value === "") return null;
  return h("div", { class: "kv" }, h("dt", { text: label }), h("dd", {}, value));
}

// Столбики по дням: стек серий (снизу вверх), подсказка на столбике, таблица под графиком.
function dayChart(days, series, caption) {
  const n = days.length;
  const totals = days.map((_, i) => series.reduce((s, x) => s + (x.values[i] || 0), 0));
  const max = Math.max(1, ...totals);
  const W = 300;
  const H = 86;
  const bw = W / n;
  const svg = svgEl("svg", { class: "daychart", viewBox: `0 0 ${W} ${H + 16}`, role: "img", "aria-label": caption });
  svgEl("line", { x1: 0, x2: W, y1: H, y2: H, class: "axis" }, svg);
  for (let i = 0; i < n; i++) {
    let y = H;
    for (const s of series) {
      const v = s.values[i] || 0;
      if (!v) continue;
      const bh = Math.max(1.5, (v / max) * (H - 4));
      svgEl("rect", { x: (i * bw + 1).toFixed(1), y: (y - bh).toFixed(1), width: Math.max(1, bw - 2).toFixed(1), height: (bh - (y < H ? 1 : 0)).toFixed(1), rx: 1.5, class: `bar ${s.cls}` }, svg);
      y -= bh;
    }
    const hit = svgEl("rect", { x: (i * bw).toFixed(1), y: 0, width: bw.toFixed(1), height: H, class: "bar-hit" }, svg);
    const parts = series.map((s) => `${s.name}: ${s.values[i] || 0}`).join(", ");
    svgEl("title", {}, hit).textContent = `${fmtDate(days[i])} — ${parts}`;
  }
  const lbl = (i, anchor) => {
    const t = svgEl("text", { x: anchor === "end" ? W : 0, y: H + 13, "text-anchor": anchor, class: "tick" }, svg);
    t.textContent = fmtDate(days[i]).slice(0, 5);
  };
  lbl(0, "start");
  lbl(n - 1, "end");
  const maxT = svgEl("text", { x: 0, y: 10, class: "tick" }, svg);
  maxT.textContent = `макс. ${max}`;

  const legend = series.length > 1
    ? h("div", { class: "chart-legend" }, series.map((s) => h("span", { class: "lg" }, h("i", { class: `sw ${s.cls}` }), s.name)))
    : null;
  const table = h("table", { class: "vtable" },
    h("caption", { text: caption }),
    h("thead", {}, h("tr", {}, h("th", { text: "день" }), series.map((s) => h("th", { text: s.name })))),
    h("tbody", {}, days.map((d, i) => (totals[i] ? h("tr", {}, h("td", { text: fmtDate(d) }), series.map((s) => h("td", { text: String(s.values[i] || 0) }))) : null)).filter(Boolean)),
  );
  const empty = totals.every((t) => !t);
  return h("figure", { class: "chart" },
    h("figcaption", { text: caption }),
    empty ? h("p", { class: "muted", text: "событий в окне нет" }) : svg,
    legend,
    empty ? null : h("details", { class: "values" }, h("summary", { text: "Таблица значений" }), table),
  );
}

function flowLink(view, f, dir, select) {
  const other = view.nodeById.get(dir === "out" ? f.to : f.from);
  const kind = view.catalog.flowKinds.get(f.kind)?.name || f.kind;
  return h("li", {},
    h("button", { type: "button", class: "link", on: { click: () => select(`f:${f.id}`) } },
      h("i", { class: `sw drv-${f.driver}`, "aria-hidden": "true" }),
      `${dir === "out" ? "→" : "←"} ${other.name}`),
    h("span", { class: "muted", text: ` ${kind} · ${STATE_NAMES[f.state] || f.state}` }));
}

function refsList(refs) {
  if (!refs || !refs.length) return null;
  return h("details", { class: "refs" }, h("summary", { text: "Источники" }), h("ul", {}, refs.map((r) => h("li", { text: r }))));
}

function nodePanel(view, n, select) {
  const cat = view.catalog;
  const layer = view.layers.find((l) => l.id === n.layer);
  const kind = cat.nodeKinds.get(n.kind)?.name || n.kind;
  const vis = cat.visibility.get(n.visibility)?.name;
  const act = STATE_NAMES[n.activity] || n.activity;
  const items = [];
  items.push(h("p", { class: "lead", text: n.role || "" }));
  const dl = h("dl", { class: "kvs" },
    row("Вид", `${kind}${layer ? " · " + layer.name : ""}`),
    row("Код", vis || null),
    row("Стадия", n.stage || null),
    row("По модели", cat.statuses.get(n.status)?.name || n.status),
    row("Сейчас", view.hasState ? `${act}${n.last ? ` · последнее событие ${fmtDateTime(n.last)} (${fmtAge(n.last)})` : ""}` : "нет среза"),
    n.note ? row("Заметка", n.note) : null,
  );
  items.push(dl);
  if (n.git) {
    const g = n.git;
    const ai = g.window?.ai || 0;
    const human = g.window?.human || 0;
    items.push(h("dl", { class: "kvs" },
      row("Основная ветка", g.head_time || g.head_date ? `последний коммит ${fmtDateTime(g.head_time || g.head_date)} (${fmtAge(g.head_time || g.head_date)})` : "нет коммитов"),
      row("Первый коммит", g.first_time || g.first_date ? fmtDate(g.first_time || g.first_date) : null),
      row(`За ${view.days.length} дней`, `${fmtNum(ai + human)} коммитов, из них ИИ ${fmtShare(ai, ai + human)}${g.window?.merges !== undefined ? `; вливаний ${fmtNum(g.window.merges)}` : ""}`),
      n.branches.known ? row("Ветки с невлитой работой", n.branches.count ? String(n.branches.count) : "нет") : null,
      g.history && g.history !== "complete" ? row("История", "неполная (клон с ограниченной глубиной)") : null,
    ));
    if (n.branches.list.length) {
      items.push(h("ul", { class: "branches" }, n.branches.list.map((b) => h("li", {}, h("code", { text: b.name }), h("span", { class: "muted", text: ` +${b.ahead} · ${fmtDateTime(b.time)}` })))));
    }
    items.push(dayChart(view.days, [
      { name: "ИИ", cls: "drv-ai", values: n.daysAi },
      { name: "человек", cls: "drv-human", values: n.daysHuman },
    ], `Коммиты основной ветки по дням, ${fmtDate(view.days[0])}–${fmtDate(view.days[view.days.length - 1])}`));
  } else if (n.kind === "actor" && sum(n.daysTotal)) {
    const isAuthor = n.id === "author";
    items.push(dayChart(view.days, [{ name: isAuthor ? "вливания и коммиты" : "коммиты сессий", cls: isAuthor ? "drv-human" : "drv-ai", values: n.daysTotal }],
      `${isAuthor ? "Решения автора в git" : "Работа сессий"} по дням`));
  }
  const out = view.outgoing.get(n.id) || [];
  const inc = view.incoming.get(n.id) || [];
  if (out.length) items.push(h("h3", { text: `Исходящие потоки · ${out.length}` }), h("ul", { class: "flowlist" }, out.map((f) => flowLink(view, f, "out", select))));
  if (inc.length) items.push(h("h3", { text: `Входящие потоки · ${inc.length}` }), h("ul", { class: "flowlist" }, inc.map((f) => flowLink(view, f, "in", select))));
  items.push(refsList(n.refs));
  return { title: n.name, body: items };
}

function flowPanel(view, f, select) {
  const cat = view.catalog;
  const a = view.nodeById.get(f.from);
  const b = view.nodeById.get(f.to);
  const drv = cat.drivers.get(f.driver)?.name || f.driver;
  const items = [];
  items.push(h("p", { class: "lead", text: f.what || "" }));
  items.push(h("p", { class: "ends" },
    h("button", { type: "button", class: "link", on: { click: () => select(`n:${a.id}`) }, text: a.name }),
    f.bidirectional ? " ⇄ " : " → ",
    h("button", { type: "button", class: "link", on: { click: () => select(`n:${b.id}`) }, text: b.name })));
  items.push(h("dl", { class: "kvs" },
    row("Вид", cat.flowKinds.get(f.kind)?.name || f.kind),
    row("Кто движет", h("span", {}, h("i", { class: `sw drv-${f.driver}`, "aria-hidden": "true" }), drv)),
    row("По модели", cat.statuses.get(f.status)?.name || f.status),
    row("По данным", view.hasState ? STATE_NAMES[f.state] || f.state : "нет среза"),
    row("Путь", cat.transports.get(f.transport)?.name || f.transport),
    row("Когда", f.trigger || null),
    f.contracts && f.contracts.length ? row("Контракт", f.contracts.join(", ")) : null,
    row("Последнее событие", f.lastEvent ? `${fmtDateTime(f.lastEvent)} (${fmtAge(f.lastEvent)})` : view.hasState && ["flowing", "quiet"].includes(f.state) ? "в окне не было" : null),
    view.hasState && f.total !== undefined && ["flowing", "quiet"].includes(f.state) ? row("События", `за ${view.rateDays} дней — ${f.week}, за ${view.days.length} — ${f.total}`) : null,
  ));
  if (["flowing", "quiet"].includes(f.state)) {
    items.push(dayChart(view.days, [{ name: "события", cls: `drv-${f.driver}`, values: f.days }], "События потока по дням"));
  } else if (f.state === "unobserved") {
    items.push(h("p", { class: "muted", text: "Сигнала у этого потока нет: он не наблюдается по устройству, а не «ноль»." }));
  } else if (f.state === "unknown") {
    items.push(h("p", { class: "muted", text: "Сигнал есть, но наблюдение не удалось — «неизвестно», а не «ноль»." }));
  }
  items.push(refsList(f.refs));
  return { title: `${a.name} → ${b.name}`, body: items };
}

// ---- tables.js
// Вкладки «Таблицы» (F-29) и «Сверка» (F-30): всё, что видно на графе, читается без графа.


// Подпись столбца — у каждой ячейки: на узком месте строка таблицы становится карточкой
// «подпись — значение», и прокрутки вбок нет (D-16, style.css).
function labelCells(table) {
  const heads = [...table.querySelectorAll("thead th")].map((th) => th.textContent);
  for (const tr of table.querySelectorAll("tbody tr")) {
    [...tr.children].forEach((cell, i) => {
      if (cell.tagName === "TD" && heads[i]) cell.setAttribute("data-label", heads[i]);
    });
  }
  return table;
}

function tablesView(view, vis, select) {
  const cat = view.catalog;
  const nodes = view.nodes.filter((n) => vis.nodes.has(n.id)).sort((a, b) => a.layerIndex - b.layerIndex || a.name.localeCompare(b.name, "ru"));
  const flows = view.flows.filter((f) => vis.flows.has(f.id)).sort((a, b) => b.week - a.week || a.id.localeCompare(b.id));
  const layerName = (id) => view.layers.find((l) => l.id === id)?.name || id;
  const pick = (sel) => ({ click: () => select(sel, true) });

  const nodeTable = h("table", { class: "vtable wide" },
    h("caption", { text: `Узлы · ${nodes.length}` }),
    h("thead", {}, h("tr", {}, ["Узел", "Слой", "Вид", "По модели", "Сейчас", "Последнее", `Коммиты за ${view.rateDays} дн.`, `за ${view.days.length} дн.`, "ИИ / человек", view.hasBranches ? "Ветки" : null].filter(Boolean).map((t) => h("th", { scope: "col", text: t })))),
    h("tbody", {}, nodes.map((n) => {
      const ai = n.git?.window?.ai ?? (n.id === "author" ? 0 : sum(n.daysAi));
      const hu = n.git?.window?.human ?? sum(n.daysHuman);
      return h("tr", {},
        h("th", { scope: "row" }, h("button", { type: "button", class: "link", on: pick(`n:${n.id}`), text: n.name })),
        h("td", { text: layerName(n.layer) }),
        h("td", { text: cat.nodeKinds.get(n.kind)?.name || n.kind }),
        h("td", { text: cat.statuses.get(n.status)?.name || n.status }),
        h("td", { text: STATE_NAMES[n.activity] || n.activity }),
        h("td", { text: n.last ? fmtDate(n.last) : "—" }),
        h("td", { class: "num", text: n.kind === "repo" || n.kind === "actor" ? fmtNum(n.week) : "—" }),
        h("td", { class: "num", text: n.kind === "repo" || n.kind === "actor" ? fmtNum(n.windowTotal) : "—" }),
        h("td", { class: "num", text: n.git ? `${fmtNum(ai)} / ${fmtNum(hu)}` : "—" }),
        view.hasBranches ? h("td", { class: "num", text: n.kind === "repo" ? String(n.branches.count) : "—" }) : null,
      );
    })),
  );

  const flowTable = h("table", { class: "vtable wide" },
    h("caption", { text: `Потоки · ${flows.length}` }),
    h("thead", {}, h("tr", {}, ["Откуда → куда", "Вид", "Кто движет", "По модели", "По данным", `За ${view.rateDays} дн.`, `за ${view.days.length} дн.`, "Последнее"].map((t) => h("th", { scope: "col", text: t })))),
    h("tbody", {}, flows.map((f) => h("tr", {},
      h("th", { scope: "row" }, h("button", { type: "button", class: "link", on: pick(`f:${f.id}`), text: `${view.nodeById.get(f.from).name} → ${view.nodeById.get(f.to).name}` })),
      h("td", { text: cat.flowKinds.get(f.kind)?.name || f.kind }),
      h("td", {}, h("i", { class: `sw drv-${f.driver}`, "aria-hidden": "true" }), cat.drivers.get(f.driver)?.name || f.driver),
      h("td", { text: cat.statuses.get(f.status)?.name || f.status }),
      h("td", { text: STATE_NAMES[f.state] || f.state }),
      h("td", { class: "num", text: ["flowing", "quiet"].includes(f.state) ? fmtNum(f.week) : "—" }),
      h("td", { class: "num", text: ["flowing", "quiet"].includes(f.state) ? fmtNum(f.total) : "—" }),
      h("td", { text: f.lastEvent ? fmtDate(f.lastEvent) : "—" }),
    ))),
  );
  const note = h("p", { class: "muted", text: "«Неизвестно» — сигнал есть, наблюдение не удалось; «не наблюдается» — сигнала нет по устройству; ни то, ни другое не ноль. Фильтры схемы действуют и здесь." });
  return h("div", { class: "tables" }, note, h("div", { class: "scroll" }, labelCells(nodeTable)), h("div", { class: "scroll" }, labelCells(flowTable)));
}

function reconView(view) {
  const out = [];
  const reg = view.registry;
  if (reg) {
    out.push(h("h3", { text: "Сверка с реестром DPmeta" }));
    out.push(h("dl", { class: "kvs" },
      h("div", { class: "kv" }, h("dt", { text: "Реестр" }), h("dd", { text: reg.checked ? `прочитан (${reg.ref || "?"}), репозиториев ${reg.registry_repos ?? "?"}` : "не прочитан" })),
      h("div", { class: "kv" }, h("dt", { text: "Контракты" }), h("dd", { text: `${(reg.contracts_covered || []).length} из ${(reg.contracts || []).length} покрыты потоками` })),
    ));
    const list = (title, items) => (items && items.length ? [h("h4", { text: `${title} · ${items.length}` }), h("ul", {}, items.map((x) => h("li", {}, h("code", { text: x }))))] : []);
    out.push(...list("В реестре есть, в модели нет", reg.missing_in_model));
    out.push(...list("В модели есть, в реестре нет", reg.not_in_registry));
    const skipped = [...(reg.excluded || []), ...(reg.contracts_excluded || []).map((c) => `DPmeta:${c}`)];
    out.push(...list("Вне сверки", skipped));
    if (skipped.length && reg.exclude_reason) out.push(h("p", { class: "muted", text: `Почему: ${reg.exclude_reason}` }));
  }
  const diags = view.diagnostics || [];
  out.push(h("h3", { text: `Диагностика сборщика · ${diags.length}` }));
  if (!diags.length) out.push(h("p", { class: "muted", text: "Записей нет." }));
  const groups = new Map();
  for (const d of diags) {
    if (!groups.has(d.code)) groups.set(d.code, []);
    groups.get(d.code).push(d);
  }
  for (const [code, list] of groups) {
    out.push(h("h4", {}, h("code", { text: code }), ` · ${list.length}`));
    out.push(h("ul", {}, list.map((d) => h("li", {}, h("code", { text: d.subject }), ` — ${d.message}`))));
  }
  return h("div", { class: "recon" }, out);
}

// ---- main.js
// Просмотрщик DPvisualisation: сборка экрана и связь частей (ТЗ §6.4, §9).
// Данные: data-src у корня → встроенный JSON (#dpvis-data) → ?model=&state= → ../data/.


const THEME_KEY = "dpvis-theme";
const LIGHT_QUERY = "(prefers-color-scheme: light)";

/**
 * Тема схемы: выбор человека кнопкой (`stored`) — главный; иначе — тема
 * страницы-хозяина (`host`); `auto` — настройка системы (`prefersLight`),
 * так её задаёт сайт автора (SocialMediaImage:Д49). Неизвестное — тёмная.
 */
function themeFor(stored, host, prefersLight) {
  const t = stored || host;
  if (t === "light" || t === "dark") return t;
  if (t === "auto") return prefersLight ? "light" : "dark";
  return "dark";
}

function prefersLight() {
  return typeof matchMedia === "function" && matchMedia(LIGHT_QUERY).matches;
}

function storeGet(k) {
  try {
    return localStorage.getItem(k);
  } catch {
    return null;
  }
}
function storeSet(k, v) {
  try {
    localStorage.setItem(k, v);
  } catch {
    /* приватное окно — тема просто не запомнится */
  }
}

function sameOrigin(url) {
  try {
    return new URL(url, location.href).origin === location.origin;
  } catch {
    return false;
  }
}

async function fetchJson(url) {
  const r = await fetch(url, { cache: "no-store" });
  if (!r.ok) throw new DataError(`${url}: ответ ${r.status}`);
  return r.json();
}

// Применить «показ» (F-32): имена закрытых-неназываемых и ветки скрыты.
function showMode(model, state) {
  const m = { ...model, nodes: model.nodes.map((n) => (n.visibility === "undisclosed" ? { ...n, name: "закрытый проект", role: "закрытый проект без публичного имени", stage: null, refs: [], repo: null } : n)) };
  let s = state;
  if (state) {
    s = { ...state, nodes: {} };
    for (const [id, v] of Object.entries(state.nodes)) {
      s.nodes[id] = v.git ? { ...v, git: { ...v.git, branches: Array.isArray(v.git.branches) ? v.git.branches.length : v.git.branches } } : v;
    }
  }
  return { model: m, state: s };
}

class Viewer {
  constructor(root) {
    this.root = root;
    this.site = root.dataset.embed === "site";
    this.data = { model: null, state: null, public: false };
    this.f = decode(location.hash);
    this.graph = null;
    this.view = null;
    this.vis = null;
    this.playTimer = 0;
    this.themeChosen = false;
    this.buildShell();
  }

  // ------------------------------------------------------------ каркас
  buildShell() {
    const r = this.root;
    r.classList.add("dpvis");
    const host = r.dataset.theme;
    r.dataset.theme = themeFor(storeGet(THEME_KEY), host, prefersLight());
    // «auto» без выбора человека — вслед за настройкой системы, без перезагрузки страницы.
    if (host === "auto" && typeof matchMedia === "function") {
      matchMedia(LIGHT_QUERY).addEventListener("change", () => {
        // Выбор кнопкой — и в памяти: без хранилища браузера (приватный режим) система его не перебивает.
        if (this.themeChosen || storeGet(THEME_KEY)) return;
        r.dataset.theme = themeFor(null, "auto", prefersLight());
        this.updateThemeBtn();
      });
    }
    r.replaceChildren();
    this.el = {};
    const e = this.el;
    e.asof = h("span", { class: "dv-asof" });
    e.stale = h("span", { class: "dv-stale", hidden: true, text: "устарел" });
    e.live = h("span", { class: "dv-live", hidden: true });
    e.theme = h("button", { type: "button", class: "dv-btn", on: { click: () => this.toggleTheme() } });
    e.show = h("button", { type: "button", class: "dv-btn", hidden: true, "aria-pressed": "false", on: { click: () => this.setF({ show: !this.f.show }, true) }, text: "Показ" });
    e.file = h("input", { type: "file", accept: ".json,application/json", class: "dv-file", on: { change: (ev) => this.openFile(ev) } });
    e.open = h("button", { type: "button", class: "dv-btn", hidden: this.site, on: { click: () => e.file.click() }, text: "Открыть…" });
    e.title = h("strong", { class: "dv-name" });
    r.appendChild(h("header", { class: "dv-head" },
      h("div", { class: "dv-title" }, e.title, e.asof, e.stale, e.live),
      h("div", { class: "dv-tools" }, e.theme, e.show, e.open, e.file)));

    e.tabs = {};
    const tabs = h("div", { class: "dv-tabs", role: "tablist", "aria-label": "Вид" });
    for (const [id, name] of [["graph", "Схема"], ["tables", "Таблицы"], ["recon", "Сверка"]]) {
      e.tabs[id] = h("button", { type: "button", role: "tab", class: "dv-tab-btn", id: `dv-tab-${id}`, on: { click: () => this.setF({ tab: id }) }, text: name });
      tabs.appendChild(e.tabs[id]);
    }
    r.appendChild(tabs);
    e.msg = h("div", { class: "dv-msg", role: "status", hidden: true });
    r.appendChild(e.msg);

    // схема
    e.filters = h("details", { class: "dv-filters" });
    e.graphBox = h("div", { class: "dv-graph" });
    e.zoomIn = h("button", { type: "button", class: "dv-btn", "aria-label": "Крупнее", on: { click: () => this.graph?.zoomBy(ZOOM.step) }, text: "+" });
    e.zoomOut = h("button", { type: "button", class: "dv-btn", "aria-label": "Мельче", on: { click: () => this.graph?.zoomBy(1 / ZOOM.step) }, text: "−" });
    e.zoomFit = h("button", { type: "button", class: "dv-btn", on: { click: () => this.graph?.fit() }, text: "Вся схема" });
    e.zoom = h("div", { class: "dv-zoom", role: "group", "aria-label": "Масштаб" }, e.zoomIn, e.zoomOut, e.zoomFit);
    e.panel = h("aside", { class: "dv-panel", "aria-live": "polite", "aria-label": "Подробности", hidden: true });
    e.hint = h("p", { class: "dv-hint", text: "Нажмите проект или связь — появятся подробности. «+» и «−» — масштаб (увеличенную схему можно двигать), «Вся схема» — вернуть. Клавиши: Tab, Enter, Esc, / — поиск, ← → — день." });
    e.timeline = h("div", { class: "dv-timeline" });
    e.legend = h("div", { class: "dv-legend", "aria-label": "Легенда" });
    e.tabGraph = h("section", { class: "dv-tab", role: "tabpanel", "aria-labelledby": "dv-tab-graph" },
      e.filters,
      (e.main = h("div", { class: "dv-main" }, h("div", { class: "dv-graph-wrap" }, e.zoom, e.graphBox), e.panel)),
      e.hint, e.timeline, e.legend);
    e.tabTables = h("section", { class: "dv-tab", role: "tabpanel", "aria-labelledby": "dv-tab-tables", hidden: true });
    e.tabRecon = h("section", { class: "dv-tab", role: "tabpanel", "aria-labelledby": "dv-tab-recon", hidden: true });
    r.append(e.tabGraph, e.tabTables, e.tabRecon);
    e.tip = h("div", { class: "dv-tip", role: "tooltip", hidden: true });
    r.appendChild(e.tip);
    this.updateThemeBtn();

    window.addEventListener("hashchange", () => {
      if (location.hash === encode(this.f)) return;
      this.f = decode(location.hash, this.view);
      this.render();
    });
    document.addEventListener("keydown", (ev) => this.onKey(ev));
    window.addEventListener("message", (ev) => {
      if (ev.source !== window.parent || window.parent === window) return;
      if (ev.data && ev.data.type === "dpvis:data") this.accept({ model: ev.data.model, state: ev.data.state || null });
    });
  }

  message(text, kind = "error") {
    const m = this.el.msg;
    m.textContent = text || "";
    m.dataset.kind = kind;
    m.hidden = !text;
  }

  // ------------------------------------------------------------ данные
  async load() {
    const r = this.root;
    const params = new URLSearchParams(location.search);
    try {
      if (r.dataset.src) {
        this.accept(classify(await fetchJson(r.dataset.src)), { stateUrl: null });
        return;
      }
      const inline = document.getElementById("dpvis-data");
      if (inline) {
        const doc = JSON.parse(inline.textContent);
        this.accept(doc.schema ? classify(doc) : { model: doc.model, state: doc.state || null });
        return;
      }
      const mUrl = params.get("model") || "../data/model.json";
      const sUrl = params.get("state") || "../data/state/latest.json";
      if (!sameOrigin(mUrl) || !sameOrigin(sUrl)) throw new DataError("адреса ?model= и ?state= — только с того же источника, что страница");
      const model = classify(await fetchJson(mUrl)).model;
      let state = null;
      try {
        state = classify(await fetchJson(sUrl)).state;
      } catch {
        state = null; // нет среза — одна модель с пометкой «нет данных» (F-31)
      }
      this.accept({ model, state }, { stateUrl: sUrl });
      const poll = Number(params.get("poll") ?? (location.protocol.startsWith("http") ? 60 : 0));
      if (poll > 0) this.startPolling(sUrl, poll);
    } catch (err) {
      this.message(`Данные не загрузились: ${err.message}. Можно открыть файл модели или среза кнопкой «Открыть…».`);
      this.el.open.hidden = false;
    }
  }

  startPolling(url, sec) {
    this.el.live.hidden = false;
    this.el.live.textContent = "⟳ живой";
    setInterval(async () => {
      try {
        const st = classify(await fetchJson(url)).state;
        if (st && st.as_of !== this.data.state?.as_of) {
          this.data.state = st;
          this.rebuild(true);
          this.el.live.textContent = `⟳ обновлено ${fmtDateTime(st.as_of)}`;
        }
      } catch {
        this.el.live.textContent = "⟳ нет связи с сервером";
      }
    }, sec * 1000);
  }

  accept(parts) {
    if (parts.model) this.data.model = parts.model;
    if ("state" in parts && parts.state !== undefined) this.data.state = parts.state;
    if (parts.public) this.data.public = true;
    if (!this.data.model) {
      this.message("Срез загружен, но модели нет — откройте файл модели.", "info");
      return;
    }
    this.message("");
    this.rebuild();
  }

  async openFile(ev) {
    const file = ev.target.files && ev.target.files[0];
    ev.target.value = "";
    if (!file) return;
    try {
      const parts = classify(JSON.parse(await file.text()));
      if (parts.state && !parts.model && !this.data.model) throw new DataError("сначала нужна модель");
      this.accept(parts);
    } catch (err) {
      this.message(`Файл «${file.name}» не принят: ${err instanceof SyntaxError ? "это не JSON" : err.message}. Прежние данные не тронуты.`);
    }
  }

  // ------------------------------------------------------------ построение
  rebuild(keepView = false) {
    const { model, state } = this.f.show ? showMode(this.data.model, this.data.state) : this.data;
    let view;
    try {
      view = normalize(model, state, { public: this.data.public });
    } catch (err) {
      this.message(`Данные не прочитаны: ${err.message}`);
      return;
    }
    this.view = view;
    this.f = decode(encode(this.f), view);
    if (keepView && this.graph) {
      this.graph.setView(view); // новый срез — тот же масштаб и сдвиг (F-45)
    } else {
      this.graph?.destroy();
      this.graph = createGraph(this.el.graphBox, view, {
        select: (sel) => this.select(sel),
        selected: () => this.f.sel,
        hover: (t, ev) => this.hover(t, ev),
        zoomChanged: (k) => this.syncZoom(k),
      });
    }
    this.el.title.textContent = view.title;
    this.el.show.hidden = !view.nodes.some((n) => n.visibility === "undisclosed") && !this.f.show;
    this.el.tabs.recon.hidden = !(view.diagnostics || view.registry);
    this.buildFilters();
    this.buildTimeline();
    this.buildLegend();
    this.render();
  }

  // ------------------------------------------------------------ состояние вида
  setF(patch, rebuild = false) {
    this.f = { ...this.f, ...patch };
    const hash = encode(this.f);
    if (hash !== location.hash && !(hash === "" && location.hash === "")) {
      history.replaceState(null, "", hash || location.pathname + location.search);
    }
    if (rebuild) this.rebuild(true);
    else this.render();
  }

  select(sel, fromTable = false) {
    this.setF({ sel, ...(fromTable ? { tab: "graph" } : {}) });
    if (sel && sel[0] === "n" && fromTable) this.graph?.centerOn(sel.slice(2));
  }

  render() {
    const v = this.view;
    if (!v) return;
    const f = this.f;
    // шапка: время среза всегда видно (F-31)
    if (v.asOf && this.root.dataset.embed === "site") {
      // На сайте схема полустатичная (D-28): дата среза, без «N дней назад · устарел».
      this.el.asof.textContent = `срез на ${fmtDate(v.asOf)}`;
      this.el.stale.hidden = true;
    } else if (v.asOf) {
      this.el.asof.textContent = `срез ${fmtDateTime(v.asOf)} · ${fmtAge(v.asOf)}`;
      this.el.stale.hidden = !isStale(v.asOf);
    } else {
      this.el.asof.textContent = `модель на ${fmtDate(v.modelAsOf)} · нет данных среза`;
      this.el.stale.hidden = true;
    }
    this.el.show.setAttribute("aria-pressed", String(!!f.show));
    for (const [id, b] of Object.entries(this.el.tabs)) b.setAttribute("aria-selected", String(f.tab === id));
    this.el.tabGraph.hidden = f.tab !== "graph";
    this.el.tabTables.hidden = f.tab !== "tables";
    this.el.tabRecon.hidden = f.tab !== "recon";

    this.vis = visible(v, f);
    const focus = focusSet(v, f.sel);
    const dim = f.q ? new Set(v.nodes.filter((n) => matches(n, f.q)).map((n) => n.id)) : null;
    this.graph.update(this.vis, focus, dim, f.day);
    this.renderPanel();
    this.syncFilters();
    this.syncTimeline();
    if (f.tab === "tables") this.el.tabTables.replaceChildren(tablesView(v, this.vis, (s, t) => this.select(s, t)));
    if (f.tab === "recon") this.el.tabRecon.replaceChildren(reconView(v));
  }

  renderPanel() {
    const v = this.view;
    const sel = this.f.sel;
    const p = this.el.panel;
    if (!sel) {
      p.classList.remove("has-sel");
      this.el.main.classList.remove("has-sel");
      p.hidden = true;
      p.replaceChildren();
      return;
    }
    const id = sel.slice(2);
    const item = sel[0] === "n" ? v.nodeById.get(id) : v.flowById.get(id);
    if (!item) return;
    const { title, body } = sel[0] === "n" ? nodePanel(v, item, (s) => this.select(s)) : flowPanel(v, item, (s) => this.select(s));
    const wasHidden = p.hidden;
    p.hidden = false;
    p.classList.add("has-sel");
    this.el.main.classList.add("has-sel");
    if (wasHidden && p.getBoundingClientRect().top > (window.innerHeight || 0)) p.scrollIntoView({ block: "nearest", behavior: "auto" });
    p.replaceChildren(
      h("div", { class: "dv-panel-head" },
        h("h2", { text: title }),
        h("button", { type: "button", class: "dv-btn dv-close", "aria-label": "Закрыть подробности", on: { click: () => this.select(null) }, text: "×" })),
      ...body.filter(Boolean));
  }

  hover(t, ev) {
    const tip = this.el.tip;
    // подсказка — только для мыши: на касание отвечает панель подробностей
    if (!t || !ev || (ev.pointerType && ev.pointerType !== "mouse")) {
      tip.hidden = true;
      return;
    }
    const v = this.view;
    let lines;
    if (t.type === "node") {
      const n = t.item;
      lines = [n.name, `${v.catalog.nodeKinds.get(n.kind)?.name || n.kind} · ${STATE_NAMES[n.activity] || n.activity}`];
      if (n.kind === "repo" || n.kind === "actor") lines.push(`за ${v.rateDays} дн.: ${n.week} коммит(ов)`);
      if (n.branches.count) lines.push(`веток с невлитой работой: ${n.branches.count}`);
    } else {
      const f = t.item;
      lines = [`${v.nodeById.get(f.from).name} → ${v.nodeById.get(f.to).name}`, `${v.catalog.flowKinds.get(f.kind)?.name || f.kind} · ${STATE_NAMES[f.state] || f.state}`];
      if (["flowing", "quiet"].includes(f.state)) lines.push(`за ${v.rateDays} дн.: ${f.week} событий`);
    }
    tip.replaceChildren(...lines.map((l, i) => h(i === 0 ? "strong" : "span", { text: l })));
    tip.hidden = false;
    const box = this.root.getBoundingClientRect();
    const x = ev.clientX - box.left + 14;
    const y = ev.clientY - box.top + 14;
    tip.style.left = `${Math.min(x, box.width - 230)}px`;
    tip.style.top = `${y}px`;
  }

  syncZoom(k) {
    const e = this.el;
    e.zoomOut.disabled = k <= ZOOM.min + 1e-6;
    e.zoomFit.disabled = k <= ZOOM.min + 1e-6;
    e.zoomIn.disabled = k >= ZOOM.max - 1e-6;
  }

  // ------------------------------------------------------------ фильтры (F-27)
  buildFilters() {
    const v = this.view;
    const e = this.el;
    e.filters.open = false; // проще экран (D-16): фильтры — по нажатию
    const kinds = [...new Set(v.flows.map((f) => f.kind))];
    const states = FLOW_STATES.filter((s) => v.flows.some((f) => f.state === s));
    const layers = v.layers.filter((l) => v.nodes.some((n) => n.layer === l.id));
    e.chips = { kinds: new Map(), states: new Map(), layers: new Map() };
    const group = (title, key, items) => {
      const box = h("div", { class: "dv-chipgroup", role: "group", "aria-label": title }, h("span", { class: "dv-chipttl", text: title }));
      for (const [id, name, cls] of items) {
        const b = h("button", { type: "button", class: "dv-chip", "aria-pressed": "true", on: { click: () => this.toggleChip(key, id, items.map((x) => x[0])) } },
          cls ? h("i", { class: `sw ${cls}`, "aria-hidden": "true" }) : null, name);
        e.chips[key].set(id, b);
        box.appendChild(b);
      }
      return box;
    };
    e.search = h("input", { type: "search", class: "dv-search", placeholder: "Поиск: имя или id", "aria-label": "Поиск узла", value: this.f.q, on: { input: (ev) => this.setF({ q: ev.target.value }) } });
    e.a7 = h("input", { type: "checkbox", id: "dv-a7", on: { change: (ev) => this.setF({ a7: ev.target.checked }) } });
    e.filters.replaceChildren(
      h("summary", { text: "Фильтры" }),
      h("div", { class: "dv-filter-row" }, e.search,
        h("label", { class: "dv-check", for: "dv-a7" }, e.a7, ` только с активностью за ${v.rateDays} дн.`),
        h("button", { type: "button", class: "dv-btn", on: { click: () => this.setF({ kinds: null, states: null, layers: null, q: "", a7: false }) }, text: "Сбросить" })),
      group("Потоки", "kinds", kinds.map((k) => {
        const fk = v.catalog.flowKinds.get(k);
        return [k, fk?.name || k, `drv-${fk?.driver || "data"}`];
      })),
      group("Состояния", "states", states.map((s) => [s, STATE_NAMES[s] || s, `st-${s}`])),
      group("Слои", "layers", layers.map((l) => [l.id, l.name, null])),
    );
  }

  toggleChip(key, id, all) {
    const cur = this.f[key] ? new Set(this.f[key]) : new Set(all);
    if (cur.has(id)) cur.delete(id);
    else cur.add(id);
    this.setF({ [key]: cur.size === all.length ? null : cur });
  }

  syncFilters() {
    const e = this.el;
    if (!e.chips) return;
    for (const key of ["kinds", "states", "layers"]) {
      for (const [id, b] of e.chips[key]) b.setAttribute("aria-pressed", String(!this.f[key] || this.f[key].has(id)));
    }
    if (e.search.value !== this.f.q) e.search.value = this.f.q;
    e.a7.checked = this.f.a7;
  }

  // ------------------------------------------------------------ шкала времени (F-28)
  buildTimeline() {
    const v = this.view;
    const e = this.el;
    if (!v.hasState) {
      e.timeline.replaceChildren(h("span", { class: "muted", text: "Шкала времени — когда есть срез." }));
      e.slider = null;
      return;
    }
    const n = v.days.length;
    e.slider = h("input", { type: "range", min: 0, max: n, step: 1, class: "dv-slider", "aria-label": "День окна", on: { input: (ev) => this.setDay(Number(ev.target.value)) } });
    e.play = h("button", { type: "button", class: "dv-btn", on: { click: () => this.togglePlay() } });
    e.dayLabel = h("output", { class: "dv-day" });
    e.timeline.replaceChildren(
      h("button", { type: "button", class: "dv-btn", "aria-label": "День назад", on: { click: () => this.stepDay(-1) }, text: "◀" }),
      e.play,
      h("button", { type: "button", class: "dv-btn", "aria-label": "День вперёд", on: { click: () => this.stepDay(1) }, text: "▶" }),
      e.slider,
      e.dayLabel,
      h("button", { type: "button", class: "dv-btn", on: { click: () => this.setDay(n) }, text: "Сейчас" }));
  }

  syncTimeline() {
    const e = this.el;
    if (!e.slider) return;
    const n = this.view.days.length;
    const d = this.f.day;
    e.slider.value = String(d === null ? n : d);
    e.dayLabel.textContent = d === null ? "сейчас — по срезу" : `${fmtDate(this.view.days[d])} — события дня`;
    e.play.textContent = this.playTimer ? "❚❚ Пауза" : "▷ Воспроизвести";
  }

  setDay(i) {
    const n = this.view.days.length;
    this.setF({ day: i >= n ? null : Math.max(0, i) });
  }

  stepDay(k) {
    const n = this.view.days.length;
    const cur = this.f.day === null ? n : this.f.day;
    this.setDay(Math.min(n, Math.max(0, cur + k)));
  }

  togglePlay() {
    if (this.playTimer) {
      clearInterval(this.playTimer);
      this.playTimer = 0;
      this.syncTimeline();
      return;
    }
    if (this.f.day === null) this.setDay(0);
    this.playTimer = setInterval(() => {
      const n = this.view.days.length;
      if (this.f.day === null || this.f.day >= n - 1) {
        clearInterval(this.playTimer);
        this.playTimer = 0;
        this.setDay(n);
        return;
      }
      this.setDay(this.f.day + 1);
    }, 1000);
    this.syncTimeline();
  }

  // ------------------------------------------------------------ легенда (F-36)
  buildLegend() {
    const v = this.view;
    const drv = (v.catalogLists.drivers || []).map((d) => h("span", { class: "lg" }, h("i", { class: `ln drv-${d.id}`, "aria-hidden": "true" }), d.name));
    this.el.legend.replaceChildren(
      h("div", { class: "lg-row" }, h("span", { class: "lg-ttl", text: "Кто движет:" }), ...drv),
      h("div", { class: "lg-row" }, h("span", { class: "lg-ttl", text: "Состояние:" }),
        h("span", { class: "lg" }, h("i", { class: "ln st-flowing", "aria-hidden": "true" }), "идёт или тихо — чем толще, тем больше событий за неделю"),
        h("span", { class: "lg" }, h("i", { class: "ln st-planned", "aria-hidden": "true" }), "план"),
        h("span", { class: "lg" }, h("i", { class: "ln st-blocked", "aria-hidden": "true" }), "заблокирован или выключен")),
      h("div", { class: "lg-row" }, h("span", { class: "lg-ttl", text: "Узлы:" }),
        h("span", { class: "lg" }, h("i", { class: "nd act-working", "aria-hidden": "true" }), "работает (яркая рамка)"),
        h("span", { class: "lg" }, h("i", { class: "nd", "aria-hidden": "true" }), "без работы"),
        h("span", { class: "lg" }, h("i", { class: "nd act-unknown", "aria-hidden": "true" }, "?"), "неизвестно"),
        h("span", { class: "lg" }, h("i", { class: "nd act-unobserved", "aria-hidden": "true" }), "не наблюдается"),
        v.hasBranches ? h("span", { class: "lg" }, h("i", { class: "bd", "aria-hidden": "true" }, "3"), "ветки с невлитой работой") : null),
      v.hidden?.undisclosed
        ? h("div", { class: "lg-row" }, h("span", { class: "lg-ttl", text: "Не показано:" }),
            h("span", { class: "lg", text: `ещё ${v.hidden.undisclosed} ${v.hidden.undisclosed === 1 ? "проект" : "проекта"} без публичного имени на схеме не показан` }))
        : null,
    );
  }

  // ------------------------------------------------------------ тема и клавиатура
  toggleTheme() {
    const t = this.root.dataset.theme === "dark" ? "light" : "dark";
    this.root.dataset.theme = t;
    this.themeChosen = true;
    storeSet(THEME_KEY, t);
    this.updateThemeBtn();
  }

  updateThemeBtn() {
    this.el.theme.textContent = this.root.dataset.theme === "dark" ? "Светлая тема" : "Тёмная тема";
  }

  onKey(ev) {
    if (!this.view || ev.defaultPrevented) return;
    const t = ev.target;
    const typing = t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.isContentEditable);
    if (ev.key === "Escape") {
      if (typing) t.blur();
      this.el.tip.hidden = true;
      if (this.f.sel) this.select(null);
      return;
    }
    if (typing || ev.ctrlKey || ev.metaKey || ev.altKey) return;
    if (ev.key === "/") {
      ev.preventDefault();
      this.el.filters.open = true;
      this.el.search.focus();
    } else if (ev.key === " " && t.tagName !== "BUTTON" && !(t.getAttribute && t.getAttribute("role") === "button")) {
      if (this.f.tab !== "graph" || !this.view.hasState) return;
      ev.preventDefault();
      this.togglePlay();
    } else if ((ev.key === "ArrowLeft" || ev.key === "ArrowRight") && this.view.hasState && this.f.tab === "graph") {
      ev.preventDefault();
      this.stepDay(ev.key === "ArrowLeft" ? -1 : 1);
    }
  }
}

function start() {
  for (const root of document.querySelectorAll("[data-dpvis]")) {
    const v = new Viewer(root);
    root.dpvis = v;
    v.load();
  }
}

if (typeof document !== "undefined") {
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
  else start();
}

})();
