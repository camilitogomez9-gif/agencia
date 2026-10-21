import modal
import json
import time
from fastapi import Header, HTTPException

app = modal.App("call-audit")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "openai>=1.50.0",
        "pydantic>=2.0.0",
        "fastapi>=0.115.0",
    )
    .add_local_python_source("schema", "prompt")
)


@app.function(
    image=image,
    secrets=[
        modal.Secret.from_name("openai-api-key"),
        modal.Secret.from_name("api-auth-token"),
    ],
    timeout=120,
)
@modal.fastapi_endpoint(method="POST")
def analyze_call(body: dict, authorization: str = Header(None)) -> dict:
    import os
    from openai import OpenAI
    from schema import CallAuditInput, CallAuditOutput
    from prompt import SYSTEM_PROMPT_BASE, build_analysis_prompt

    # Bearer token auth
    expected_token = os.environ.get("API_AUTH_TOKEN")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    if authorization.replace("Bearer ", "") != expected_token:
        raise HTTPException(status_code=403, detail="Invalid authentication token")

    # Validar input
    try:
        call_input = CallAuditInput(**body)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Input inválido: {str(e)}")

    # Llamar a OpenAI con reintentos
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    user_prompt = build_analysis_prompt(call_input.transcript, call_input.business_context)

    start = time.time()
    audit_output = None
    last_error = None

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                max_tokens=4096,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT_BASE},
                    {"role": "user", "content": user_prompt},
                ],
            )

            raw_json = response.choices[0].message.content.strip()
            parsed = json.loads(raw_json)

            parsed["closer_name"] = call_input.closer_name
            parsed["call_date"] = call_input.call_date
            parsed["call_outcome"] = call_input.call_outcome.value if call_input.call_outcome else None
            parsed["duration_minutes"] = call_input.duration_minutes
            parsed["modelo_usado"] = "gpt-4.1-mini"
            parsed["procesado_en_segundos"] = round(time.time() - start, 2)

            audit_output = CallAuditOutput(**parsed)
            break

        except Exception as e:
            last_error = str(e)
            print(f"Intento {attempt + 1} fallido: {e}")
            continue

    if audit_output is None:
        raise HTTPException(
            status_code=500,
            detail=f"No se pudo procesar la llamada después de 3 intentos. Último error: {last_error}"
        )

    print(f"[AUDIT] closer={audit_output.closer_name} | date={audit_output.call_date} | score={audit_output.score_total} | tiempo={audit_output.procesado_en_segundos}s")

    return audit_output.model_dump()


@app.local_entrypoint()
def test_local():
    test_input = {
        "transcript": """
        Closer: Hola Juan, ¿cómo estás? Gracias por tomar la llamada.
        Prospecto: Bien, gracias. Tengo solo 30 minutos.
        Closer: Perfecto, vamos directo al grano. Cuéntame, ¿cuál es el mayor problema que estás teniendo ahora mismo con tus ventas?
        Prospecto: Básicamente que mis closers cierran muy poco. Tenemos leads pero no convierten.
        Closer: ¿Y cuánto tiempo llevas con este problema?
        Prospecto: Unos 6 meses.
        Closer: ¿Y eso qué impacto tiene en el negocio?
        Prospecto: Perdemos como $20k mensuales en oportunidades que no cerramos.
        Closer: Entiendo. ¿Qué han intentado hasta ahora para resolverlo?
        Prospecto: Capacitaciones básicas, pero nada específico.
        Closer: Bien. Lo que hacemos en la agencia es exactamente eso: auditar cada llamada automáticamente y darle feedback objetivo a cada closer, sin que el manager tenga que escuchar horas de grabaciones. ¿Tiene sentido para tu caso?
        Prospecto: Sí, suena interesante. ¿Cuánto cuesta?
        Closer: Estamos hablando de $2.500 mensuales. Y dado que estás perdiendo $20k, el ROI es bastante claro.
        Prospecto: Necesito consultarlo con mi socio.
        Closer: Totalmente entendible. ¿Cuándo podrías tener esa conversación con él?
        Prospecto: Esta semana.
        Closer: Perfecto. ¿Qué te parece si agendamos una llamada para el viernes con los dos para que pueda responder sus preguntas directamente?
        Prospecto: Suena bien.
        """,
        "closer_name": "Demo Closer",
        "call_date": "2026-02-18",
        "call_outcome": "pendiente",
        "duration_minutes": 25,
    }

    import httpx
    import os
    token = os.environ.get("API_AUTH_TOKEN", "test")
    # Para test local directo sin HTTP:
    print(json.dumps(test_input, indent=2, ensure_ascii=False))
