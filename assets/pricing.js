(() => {
  'use strict';
  const cards = [...document.querySelectorAll('[data-product-sku]')];
  if (!cards.length) return;
  const en = document.documentElement.lang === 'en';
  const status = document.getElementById('service-status');
  const freeSku = 'aibox_open_source';
  const field = (card, key) => card.querySelector(`[data-field="${key}"]`);
  const money = fen => '¥' + (fen / 100).toLocaleString(en ? 'en-US' : 'zh-CN', { maximumFractionDigits: 2 });
  let pending = false;
  function disablePaid() {
    cards.filter(card => card.dataset.productSku !== freeSku).forEach(card => {
      const button = field(card, 'button');
      button.removeAttribute('href');
      button.setAttribute('aria-disabled', 'true');
      button.textContent = en ? 'Checking availability…' : '正在读取商品';
    });
  }
  async function refresh() {
    if (pending) return;
    pending = true;
    disablePaid();
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 8000);
    try {
      const response = await fetch('/api/aibox' + (en ? '?lang=en' : ''), { cache: 'no-store', credentials: 'omit', signal: controller.signal });
      if (!response.ok) throw new Error('unavailable');
      const data = await response.json();
      if (!Array.isArray(data.products)) throw new Error('invalid');
      for (const card of cards) {
        const sku = card.dataset.productSku;
        const p = data.products.find(item => item.sku === sku);
        const button = field(card, 'button');
        card.hidden = p?.visible === false;
        if (!p || !Number.isSafeInteger(p.priceFen) || p.priceFen < 0 || !Array.isArray(p.features)) {
          if (sku !== freeSku) {
            field(card, 'price').textContent = '—';
            field(card, 'unit').textContent = en ? 'Unavailable' : '暂未开放';
            button.textContent = en ? 'Unavailable' : '暂未开放';
          }
          continue;
        }
        for (const key of ['name', 'eyebrow', 'description', 'notice']) field(card, key).textContent = typeof p[key] === 'string' ? p[key] : '';
        field(card, 'price').textContent = money(p.priceFen);
        field(card, 'unit').textContent = p.priceSuffix || '';
        const original = field(card, 'original');
        original.hidden = !Number.isSafeInteger(p.originalPriceFen) || p.originalPriceFen <= p.priceFen;
        original.textContent = original.hidden ? '' : money(p.originalPriceFen);
        const list = field(card, 'features');
        list.replaceChildren(...p.features.slice(0, 50).filter(item => typeof item === 'string').map(item => { const li = document.createElement('li'); li.textContent = item; return li; }));
        const badge = field(card, 'badge');
        if (badge) { badge.textContent = p.badge || ''; badge.hidden = !p.badge; }
        if (sku === freeSku) { button.textContent = p.buttonLabel || (en ? 'Open GitHub' : '前往 GitHub 自助'); continue; }
        if (p.available === true && p.priceFen > 0 && p.href === '/store?checkout=' + sku) {
          button.href = p.href;
          button.removeAttribute('aria-disabled');
          button.textContent = p.buttonLabel || (en ? 'Pay now' : '立即付款');
        } else {
          button.textContent = en ? 'Currently unavailable' : '暂未开放购买';
        }
      }
      status.textContent = en ? 'Prices and availability are synced with the store. Sign in before paying, then contact support with your email and order number.' : '价格与可售状态已同步商城。请先登录邮箱付款，再凭该邮箱和订单号联系客服。';
    } catch {
      cards.filter(card => card.dataset.productSku !== freeSku).forEach(card => {
        field(card, 'price').textContent = '—';
        field(card, 'unit').textContent = en ? 'Could not load price' : '价格暂时无法读取';
        field(card, 'original').hidden = true;
        field(card, 'button').textContent = en ? 'Please try again later' : '请稍后重试';
      });
      status.textContent = en ? 'Store information is unavailable. Refresh to retry or visit the store.' : '暂时无法读取商城信息，请刷新重试或前往主站商城查看。';
    } finally {
      clearTimeout(timer);
      pending = false;
    }
  }
  document.addEventListener('visibilitychange', () => { if (!document.hidden) void refresh(); });
  setInterval(() => { if (!document.hidden) void refresh(); }, 60000);
  void refresh();
})();
