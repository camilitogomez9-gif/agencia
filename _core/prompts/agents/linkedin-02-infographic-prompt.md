# Prompt — Generación de Infografía con Nano Banana Pro

> **Uso:** Este prompt recibe el output estructurado del paso 01 (content extraction) y genera una infografía 9:16 lista para publicar en LinkedIn. El input ya viene limpio y estructurado — no hay que interpretar nada, solo aplicar el sistema visual.

---

Create a premium 9:16 infographic (1080×1920px) using the structured content below. This is for personal branding on LinkedIn — the aesthetic must feel polished, editorial, and modern. No generic AI look.

═══ CRITICAL RULES — READ FIRST ═══
1. NEVER render font names, sizes, or style specs as visible text. All typography instructions are for YOUR rendering engine only — they must NEVER appear on the canvas.
2. NEVER duplicate or repeat any word or phrase within a card or across the design.
3. NO kicker, tagline, brand name, or "LA AGENCIA AI" text anywhere on the canvas.
4. Proofread every text element before finalizing — zero typos, zero repeated words.

═══ CONTENT MAPPING ═══
- TÍTULO → large H1 title, top zone
- CONCEPTO_CENTRAL → prominent pull-quote callout block, first in content zone
- SECCIÓN_X → card header (bold, concise)
- INSIGHT_X → card body (lighter weight, max 2 lines — trim if longer)
- HERRAMIENTA_PRINCIPAL → sets primary accent color and optional tool logo

═══ COLORS ═══
Background: #0D0D0D for technical/dark content — #F7F5F0 for educational/light content.
Primary accent by HERRAMIENTA_PRINCIPAL:
  Claude/Anthropic → #D4703A
  ChatGPT/OpenAI → #10A37F
  YouTube → #FF0000
  n8n → #EA4B26
  LinkedIn → #0077B5
  WhatsApp → #25D366
  ninguna / Generic AI → #F2CB2D
Accent usage: max 25% of canvas surface. Use only on title key words, card borders, numbered circles, divider line.
Dark bg text: #FFFFFF (headers) / rgba(255,255,255,0.72) (body).
Light bg text: #111111 (headers) / rgba(0,0,0,0.60) (body).
Card surface dark: rgba(255,255,255,0.05) with 1px border rgba(accent,0.25).
Card surface light: rgba(0,0,0,0.04) with 1px border rgba(accent,0.25).

═══ TYPOGRAPHY (style instructions only — never render these as text) ═══
Title H1: heavy weight, 68–78pt. 1–3 key words in accent color, rest in primary text color. Two-line layout preferred: first line regular weight, second line heavy weight.
CONCEPTO_CENTRAL text: semibold, 22–26pt, full accent color, generous line-height.
Card headers (SECCIÓN_X): semibold, 17–20pt, primary text color.
Card body (INSIGHT_X): regular weight, 13–15pt, 72% opacity text color, line-height 1.55. Maximum 2 lines — truncate cleanly if needed.

═══ LAYOUT ═══
Canvas: 1080×1920px. Safe margin: 72px all sides. Usable width: 936px.
Title zone: y 72–400px. Contains only the H1 title and optional tool logo (48px, top-left).
Thin 1px divider (accent color, 20% opacity) at y 420px separating title from content.
Content zone: y 440–1720px.
  — CONCEPTO_CENTRAL block: full usable width, border-radius 20px, left accent border 5px, padding 24px. Place at top of content zone with 32px margin above first card.
  — Section cards: border-radius 16px, padding 20px 24px. Card header on top, body below with 8px gap. 3 or fewer sections → single column. 4–7 sections → two-column grid (456px + 24px gutter + 456px). Minimum 16px gap between cards. Cards must NEVER touch margins or each other.
  — Decorative background number: use total section count (e.g. "5") at ~700pt, accent color at 7% opacity, centered vertically in content zone behind the cards. Must be fully contained within the content zone — never clip or bleed outside.
Signature zone: y 1740–1900px. Left-aligned, vertically centered.
  — Author photo from context image: circle crop, 52px diameter, fully contained (no clipping).
  — To the right of photo, 12px gap: handle "@agustinbadt" in regular weight ~15pt at 65% opacity.
  — Immediately after the handle, a solid blue circle (#1D9BF0) 14px diameter containing a white checkmark ✓ — this is the verified badge.
  — NO name text. NO "Agustín Badt" anywhere. ONLY photo + @agustinbadt + blue verified badge.

═══ VISUAL QUALITY ═══
- Strong whitespace rhythm — content should breathe, not feel packed.
- Visual hierarchy in each card: header clearly heavier/larger than body.
- CONCEPTO_CENTRAL should feel like the centerpiece — give it visual weight.
- One subtle decorative element maximum per zone.
- No drop shadows above 6px blur / 12% opacity.
- No gradients on text. No 3D. No stock photos. No hand-drawn elements.
- If tool logo exists, use flat version only.

Now render the infographic using this structured content:
