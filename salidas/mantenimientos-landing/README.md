# Mantenimientos Landing

Landing pública de planes de mantenimiento de la agencia.AI. Static site (HTML + CSS + React/Babel via CDN) servido desde Vercel.

**Fuente de diseño:** Claude Design handoff (junio 2026). Tokens del la agencia.AI Design System en `tokens.css`.

---

## Stack

- `index.html` — única página. Hero + Pricing (toggle mensual/anual) + Qué incluye + Comparativa + FAQ + Footer.
- `tokens.css` — design tokens de la agencia.AI (palette, tipografía, gradients, sombras).
- `tweaks-panel.jsx` — devtool flotante (acento + plan destacado + facturación). Inocuo para visitantes.
- `assets/` — favicon + logo.
- `vercel.json` — config static (cleanUrls, security headers).

**Sin framework. Sin build step. Sin backend.** Edits son directos al HTML.

---

## Decisiones tomadas

1. **Tema light fijo.** El `<html data-theme="light">` está hardcoded. El control "Tema" del Tweaks Panel fue removido para no exponer dark en prod. El CSS de dark sigue presente (no estorba) por si se reactiva en el futuro.
2. **Sin CTAs ni captura de leads.** El mantenimiento se vende **post-proyecto**, así que el canal de comunicación con el cliente ya existe. La landing es **informativa pura** — todos los botones "Elegir plan", "Hablar con un arquitecto", "Empezar con X", "Agendar diagnóstico" + la sección final "Dejá de apagar incendios" fueron removidos. Si en el futuro se quiere reusar como pieza comercial fría, hay que re-introducirlos.
3. **Tweaks panel en prod.** Útil para iterar variaciones (acento, plan destacado) sin redeploy. Si se considera ruido para visitantes, se remueve el `<script type="text/babel">` (líneas ~503-540) y el archivo `tweaks-panel.jsx`.

---

## Editar precios / features de los planes

Los 3 planes están hardcoded en `index.html`, sección `<section class="sec" id="planes">` (líneas ~265-340 aprox).

Cada tier tiene esta estructura:

```html
<div class="tier" data-tier="esencial">
  <div class="t-name">Esencial</div>
  <div>
    <div class="t-price">
      <span class="t-cur">USD</span>
      <span class="t-amt" data-m="100" data-a="83">100</span>
      <span class="t-per">/ mes</span>
    </div>
    ...
  </div>
  <p class="t-desc">...</p>
  <ul class="t-feats">
    <li>... feature 1 ...</li>
    ...
  </ul>
</div>
```

- **Precio mensual:** `data-m="100"` y el texto visible `>100<`.
- **Precio anual:** `data-a="83"` (lo que se muestra cuando el toggle "Anual" está activo).
- **Features:** cada `<li>` dentro de `<ul class="t-feats">`.

> ⚠ Los datos actuales (Esencial USD 100/83 · Pro USD 300/250 · A medida Consultar) son **placeholders** generados por el assistant de Design. Los valores reales de la lovable anterior eran: Básico USD 100 · Evolución USD 282 · Profesional USD 597. **Validar con la agencia antes de publicar como definitivo.**

También hay que actualizar la **comparativa** (sección `id="comparar"`) si cambian features o si se renombran planes.

---

## Cambiar el plan destacado ("Más elegido")

Buscar `<div class="tier feat" data-tier="pro">` y mover la clase `feat` + el `<span class="feat-badge">Más elegido</span>` al tier que corresponda. O cambiarlo en vivo desde el Tweaks Panel y copiar el resultado al HTML.

---

## Deploy

Desde esta carpeta:

```bash
vercel deploy            # preview
vercel deploy --prod     # producción
```

Primera vez:
```bash
vercel link              # crea proyecto NUEVO (no usar el linkeo del root, que es para la webapp)
```

> Importante: NO correr `vercel link` desde el root del workspace — ese proyecto está linkeado a la webapp Next.js productiva. Este proyecto se gestiona **solo desde `salidas/mantenimientos-landing/`**.

---

## Dominio custom

Configurar en Vercel Dashboard → este proyecto → Domains → Add Domain. Sugerido: `mantenimientos.[TU-DOMINIO]` (consistente con el subdominio de n8n).

DNS: CNAME → `cname.vercel-dns.com`. Cert SSL automático.

---

## Open items

- [ ] Datos reales de los 3 planes (placeholders del Design, no validados con cliente).
- [ ] Dominio custom definitivo.
- [ ] Decidir si dejar el Tweaks Panel en prod.
- [ ] OG image para shares en redes (no incluida en v1).
- [ ] Analytics (Vercel Analytics / Plausible / GA4) — no incluido en v1.

---

## Limitaciones del prototipo

- React + Babel cargan vía CDN UMD. Funciona perfecto para una landing pero **no es óptimo para SEO server-rendered**. Si la página tiene que rankear en Google y los crawlers de IA, conviene migrar a Next.js (puede vivir como ruta `/mantenimientos` dentro de `webapp/` o como proyecto Next.js separado).
- Babel standalone transpila en runtime (latencia inicial leve). Aceptable para una landing de información.
- Los tier cards perdieron sus botones — el CSS regla `margin-top:auto` en `.tier .btn` (línea ~153) quedó inerte. No molesta. Si más adelante se vuelven a agregar CTAs, el rule sigue ahí.
