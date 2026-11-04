// 各章画面。每个场景函数 (t, sc)：t = 全片时间（秒），sc = timing.js 里该场景（含 lines[i].t0/t1/text）。
// 画面只由 t 决定；时间点全部用 sc.lines / at(line, '词') 从配音推出，不手写秒数。
import { seg, lerp, clamp, ease, glide, spring, mix, rgba } from './motion.js';

export function makeScenes(ctx, C, ZH, NUM, helpers) {
  const { drawPerson } = helpers;
  // 词在句中的时间（按字符位置比例估算）。锚点词必须原样在台词里，否则返回句首。
  const at = (line, word) => {
    const i = line.text.indexOf(word);
    return line.t0 + (line.t1 - line.t0) * Math.max(0, i) / line.text.length;
  };
  const pop = (t, t0, o = { freq: 2.6, damp: 0.78 }) => spring(t - t0, o);
  const leave = (t, t1, d = 0.45) => 1 - ease.inCubic(seg(t, t1, t1 + d));
  const withA = (a, fn) => { if (a <= 0.002) return; ctx.save(); ctx.globalAlpha *= clamp(a); fn(); ctx.restore(); };
  const enter = (t, t0, fn, dy = 26, o) => {
    const k = pop(t, t0, o);
    withA(k, () => { ctx.translate(0, (1 - k) * dy); fn(k); });
  };
  function text(s, x, y, size, col = C.ink, w = 400, align = 'left', font = ZH) {
    ctx.font = font(w, size); ctx.fillStyle = col; ctx.textAlign = align; ctx.textBaseline = 'alphabetic';
    ctx.fillText(s, x, y); ctx.textAlign = 'left';
  }
  const tw = (s, size, w = 400, font = ZH) => { ctx.font = font(w, size); return ctx.measureText(s).width; };
  // 超出 maxW 时自动缩小字号（最小 24）——中英文切换不溢出
  function fitText(s, x, y, size, maxW, col, w = 400, align = 'left', font = ZH) {
    let sz = size;
    while (sz > 24 && tw(s, sz, w, font) > maxW) sz -= 1;
    text(s, x, y, sz, col, w, align, font);
  }
  function box(x, y, w, h, r, fill, stroke, lw = 2) {
    if (w <= 0 || h <= 0) return;
    ctx.beginPath(); ctx.roundRect(x, y, w, h, Math.min(r, w / 2, h / 2));
    if (fill) { ctx.fillStyle = fill; ctx.fill(); }
    if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = lw; ctx.stroke(); }
  }
  function shadowBox(x, y, w, h, r, fill, a = 0.1) {
    ctx.save(); ctx.shadowColor = rgba(C.ink, a); ctx.shadowBlur = 36; ctx.shadowOffsetY = 12;
    box(x, y, w, h, r, fill); ctx.restore();
  }
  function check(cx, cy, r, col = C.purple, k = 1) {
    ctx.fillStyle = col; ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = '#fff'; ctx.lineWidth = r * 0.22; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    ctx.beginPath(); ctx.moveTo(cx - r * 0.45, cy + r * 0.02);
    const p = clamp(k * 2); ctx.lineTo(cx - r * 0.45 + r * 0.33 * p, cy + r * 0.02 + r * 0.38 * p);
    if (k > 0.5) { const q = clamp(k * 2 - 1); ctx.lineTo(cx - r * 0.12 + r * 0.6 * q, cy + r * 0.4 - r * 0.78 * q); }
    ctx.stroke();
  }
  function arrow(x0, y0, x1, y1, k, col = C.grey, lw = 4) {
    if (k <= 0) return;
    const x = lerp(x0, x1, k), y = lerp(y0, y1, k), a = Math.atan2(y1 - y0, x1 - x0);
    ctx.strokeStyle = col; ctx.fillStyle = col; ctx.lineWidth = lw; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x, y); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(x + Math.cos(a) * 6, y + Math.sin(a) * 6);
    ctx.lineTo(x - Math.cos(a - 0.5) * 18, y - Math.sin(a - 0.5) * 18);
    ctx.lineTo(x - Math.cos(a + 0.5) * 18, y - Math.sin(a + 0.5) * 18); ctx.closePath(); ctx.fill();
  }

  const IMG = {};
  ['laws', 'lawyers', 'dash'].forEach(k => { const im = new Image(); im.src = `img/${k}.png`; IMG[k] = im; });
  helpers.images = IMG;
  function pic(im, x, y, w, h) {
    if (!im.complete || !im.naturalWidth) return;
    const s = Math.min(w / im.naturalWidth, h / im.naturalHeight), dw = im.naturalWidth * s, dh = im.naturalHeight * s;
    const dx = x + (w - dw) / 2, dy = y + (h - dh) / 2;
    shadowBox(dx - 8, dy - 8, dw + 16, dh + 16, 14, '#fff', 0.1);
    ctx.drawImage(im, dx, dy, dw, dh);
  }
  const c0 = sc => sc.t0 + 1.4;

  // 01 痛点：三张问题卡 → 大模型编造 → 目标
  function pain(t, sc) {
    const L = sc.lines;
    ['欠薪', '押金', '网购维权'].forEach((s, i) => {
      enter(t, Math.max(c0(sc), at(L[0], s)), () => {
        shadowBox(220 + i * 330, 260, 290, 150, 16, '#fff', 0.08);
        text(s, 365 + i * 330, 350, 48, C.ink, 700, 'center');
      });
    });
    enter(t, at(L[0], '请律师'), () => {
      text('请律师 = 成本高', 1380, 350, 46, C.sub, 700, 'center');
    });
    enter(t, L[1].t0, () => {
      shadowBox(220, 470, 1480, 150, 16, '#fff', 0.08);
      text('通用大模型', 270, 562, 44, C.ink, 700);
      text('《某某法》第 999 条 ……', 640, 562, 44, C.grey, 400);
      const k = glide(seg(t, at(L[1], '不存在'), at(L[1], '不存在') + 0.5));
      ctx.strokeStyle = C.orange; ctx.lineWidth = 6; ctx.beginPath(); ctx.moveTo(630, 548); ctx.lineTo(630 + 520 * k, 548); ctx.stroke();
      if (k > 0.9) text('编造法条', 1300, 562, 44, C.orange, 700);
    });
    enter(t, L[2].t0, () => {
      text('目标：回答有依据 · 依据能核对', 960, 780, 60, C.purple, 700, 'center');
    });
  }

  // 02 架构：浏览器 → 后端 → 扣子智能体，流式返回
  function arch(t, sc) {
    const L = sc.lines;
    const nodes = [['浏览器', 'Vue 3 前端', 260], ['后端', 'Spring Boot', 810], ['扣子智能体', 'Coze 平台', 1360]];
    nodes.forEach(([a, b, x], i) => {
      enter(t, Math.max(c0(sc), L[0].t0 + i * 0.5), () => {
        shadowBox(x, 380, 320, 200, 18, i === 2 ? C.purple : '#fff', 0.1);
        text(a, x + 160, 470, 46, i === 2 ? '#fff' : C.ink, 700, 'center');
        text(b, x + 160, 530, 32, i === 2 ? '#E6E2EC' : C.sub, 400, 'center');
      });
    });
    const k1 = glide(seg(t, at(L[1], '提问'), at(L[1], '提问') + 0.6));
    const k2 = glide(seg(t, at(L[1], '代理'), at(L[1], '代理') + 0.6));
    arrow(590, 440, 800, 440, k1, C.purple);
    arrow(1140, 440, 1350, 440, k2, C.purple);
    if (t > at(L[1], '令牌')) enter(t, at(L[1], '令牌'), () => {
      box(810, 660, 320, 64, 10, rgba(C.orange, 0.12)); text('令牌只在后端', 970, 704, 32, C.orange, 700, 'center');
    });
    if (t > L[2].t0) {
      const p = (t - L[2].t0) * 0.9;
      for (let j = 0; j < 5; j++) {
        const f = ((p + j * 0.2) % 1);
        ctx.fillStyle = rgba(C.orange, 1 - f * 0.4);
        ctx.beginPath(); ctx.arc(lerp(1500, 420, f), 612, 9, 0, Math.PI * 2); ctx.fill();
      }
      enter(t, L[2].t0, () => text('流式返回 · 边生成边显示', 960, 820, 48, C.purple, 700, 'center'));
    }
  }

  // 03 知识库与人设
  function kb(t, sc) {
    const L = sc.lines;
    const laws = ['民法典', '劳动合同法', '劳动法', '劳动争议调解仲裁法', '消费者权益保护法', '道路交通安全法'];
    withA(leave(t, L[2].t0 - 0.5, 0.5), () => {
      laws.forEach((s, i) => enter(t, Math.max(c0(sc), L[0].t0 + 0.8 + i * 0.25), () => {
        const x = 200 + (i % 3) * 520, y = 270 + Math.floor(i / 3) * 140;
        shadowBox(x, y, 480, 110, 14, '#fff', 0.08);
        fitText(s, x + 240, y + 70, 38, 440, C.ink, 700, 'center');
      }));
      if (t > L[1].t0) enter(t, L[1].t0, () => {
        const n = Math.round(1706 * glide(seg(t, at(L[1], '共'), at(L[1], '共') + 1.2)));
        text(String(n), 960, 760, 140, C.orange, 700, 'center', NUM);
        text('条法条 · 一条一个片段', 960, 830, 40, C.sub, 400, 'center');
      });
    });
    if (t > L[2].t0 - 0.5) {
      ['问题分析', '法律依据', '处理建议', '风险提示'].forEach((s, i) => enter(t, Math.max(L[2].t0, at(L[2], s)), () => {
        const x = 200 + i * 390;
        shadowBox(x, 380, 350, 200, 18, i === 1 ? C.purple : '#fff', 0.1);
        text(String(i + 1), x + 175, 450, 48, i === 1 ? '#fff' : C.purple, 700, 'center', NUM);
        text(s, x + 175, 530, 44, i === 1 ? '#fff' : C.ink, 700, 'center');
      }));
      enter(t, L[2].t0 + 0.6, () => text('人设规定的回答结构', 960, 720, 40, C.sub, 400, 'center'));
    }
  }

  // 04 演示：聊天窗口
  function demo(t, sc) {
    const L = sc.lines;
    const steps = ['提问', '问题分析', '法律依据', '处理建议', '风险提示'];
    const starts = [L[0].t0, L[1].t0, at(L[1], '劳动合同法'), L[2].t0, L[3].t0];
    steps.forEach((s, i) => {
      const x = 640 + i * 205, on = t >= starts[i], cur = on && (i === 4 || t < starts[i + 1]);
      box(x, 92, 190, 52, 26, cur ? C.orange : on ? C.purple : C.ghost);
      text(s, x + 95, 128, 26, on ? '#fff' : C.sub, 700, 'center');
    });
    shadowBox(260, 175, 1400, 760, 20, '#fff', 0.1);
    enter(t, Math.max(c0(sc), at(L[0], '用户问')), () => {
      box(840, 210, 790, 70, 35, C.purple);
      fitText('入职半年公司一直不签劳动合同，能要求什么？', 1235, 256, 30, 740, '#fff', 400, 'center');
    }, 14);
    const blocks = [
      [L[1].t0, '问题分析', '入职半年未签书面劳动合同，用人单位违反订立规定。'],
      [at(L[1], '劳动合同法'), '法律依据', '《劳动合同法》第十条 · 第八十二条（超过一个月不满一年未签，每月支付二倍工资）'],
      [L[2].t0, '处理建议', '先协商补签；不成就向劳动监察投诉或申请劳动仲裁，主张二倍工资差额。'],
      [L[3].t0, '风险提示', '注意仲裁时效。以上内容仅供参考，不构成正式法律意见。'],
    ];
    blocks.forEach(([t0, h, b], i) => {
      if (t < t0) return;
      enter(t, t0, () => {
        const y = 320 + i * 150;
        ctx.fillStyle = i === 1 ? C.orange : C.purple; ctx.fillRect(300, y, 6, 110);
        text(h, 330, y + 40, 34, C.ink, 700);
        const shown = Math.floor(b.length * clamp((t - t0) / 1.6));
        fitText(b.slice(0, shown), 330, y + 92, 30, 1290, C.sub, 400);
      }, 14);
    });
  }

  // 05 三类用户：截图轮播
  function func(t, sc) {
    const L = sc.lines;
    const roles = [['咨询用户', '查法条 · 文书模板 · 预约律师'], ['律师', '资质认证 · 处理预约'], ['管理员', '审核 · 数据统计']];
    roles.forEach(([r, d], i) => enter(t, Math.max(c0(sc), L[0].t0 + 0.8 + i * 0.3), () => {
      const y = 260 + i * 200;
      shadowBox(150, y, 560, 160, 16, '#fff', 0.08);
      ctx.fillStyle = C.purple; ctx.fillRect(150, y, 8, 160);
      text(r, 190, y + 65, 42, C.ink, 700);
      fitText(d, 190, y + 120, 30, 500, C.sub, 400);
    }));
    const anchors = [L[1].t0, at(L[1], '律师可以'), at(L[1], '管理员')];
    const keys = ['laws', 'lawyers', 'dash'];
    let k = 0; anchors.forEach((a, i) => { if (t >= a) k = i; });
    if (t >= L[1].t0) enter(t, anchors[k], () => pic(IMG[keys[k]], 790, 230, 1000, 660), 20);
  }

  // 06 测试数字
  function test(t, sc) {
    const L = sc.lines;
    const cards = [
      [Math.max(c0(sc), L[0].t0 + 0.4), '28/28', '功能测试全部通过', C.purple],
      [at(L[1], '调整后'), '9.14→0.37 s', '50 人并发首个响应', C.purple],
      [at(L[2], '正确率'), '86%', '法律依据正确率（43/50）', C.orange],
      [at(L[2], '非法律'), '10/10', '非法律问题全部拒答', C.purple],
    ];
    cards.forEach(([t0, n, d, col], i) => enter(t, t0, () => {
      const x = 170 + (i % 2) * 820, y = 260 + Math.floor(i / 2) * 330;
      shadowBox(x, y, 760, 280, 18, '#fff', 0.08);
      fitText(n, x + 380, y + 150, 110, 700, col, 700, 'center', NUM);
      text(d, x + 380, y + 225, 36, C.sub, 400, 'center');
    }, 30));
  }

  // 07 对照实验：柱状
  function compare(t, sc) {
    const L = sc.lines;
    enter(t, Math.max(c0(sc), L[0].t0 + 0.5), () => {
      text('知识库组', 520, 300, 40, C.purple, 700, 'center');
      text('对照组（无知识库）', 1400, 300, 40, C.sub, 700, 'center');
    });
    const bar = (x, v, max, col, t0, label) => {
      const k = glide(seg(t, t0, t0 + 0.8)), h = 300 * v / max * k;
      box(x - 70, 720 - h, 140, h, 8, col);
      if (k > 0.6) text(label, x, 700 - h, 40, col === C.grey ? C.sub : col, 700, 'center', NUM);
    };
    const tA = L[1].t0, tB = L[2].t0;
    withA(leave(t, tB - 0.4, 0.4), () => {
      bar(520, 86, 100, C.purple, tA, '86%');
      bar(1400, 78, 100, C.grey, tA, '78%');
      if (t > at(L[1], '不显著')) enter(t, at(L[1], '不显著'), () => text('差异不显著（p≈0.39）', 960, 820, 40, C.sub, 700, 'center'));
      enter(t, tA, () => text('法律依据正确率', 960, 900, 32, C.sub, 400, 'center'));
    });
    if (t > tB - 0.4) {
      bar(520, 21, 60, C.purple, at(L[2], '五十三'), '21 条');
      bar(1400, 53, 60, C.grey, at(L[2], '五十三'), '53 条');
      enter(t, tB, () => text('引用知识库以外的规定', 960, 900, 32, C.sub, 400, 'center'));
      if (t > at(L[2], '更容易')) enter(t, at(L[2], '更容易'), () => text('回答更容易核对', 960, 820, 44, C.orange, 700, 'center'));
    }
  }

  // ───────── 片尾 ─────────
  function end(t, sc) {
    const L = sc.lines;
    enter(t, sc.t0 + 0.2, () => {
      const s = L[0].text.replace(/[。.]$/, ''), w = tw(s, 80, 700);
      text(s, 960, 500, 80, C.ink, 700, 'center');
      ctx.fillStyle = C.orange; ctx.fillRect(960 - w / 2, 540, w * glide(seg(t, sc.t0 + 0.6, sc.t0 + 1.4)), 6); // 长度跟随文字
    }, 30);
  }

  return { s01_pain: pain, s02_arch: arch, s03_kb: kb, s04_demo: demo, s05_func: func,
           s06_test: test, s07_compare: compare, s09_end: end };
}
