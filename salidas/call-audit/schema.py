from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class CallOutcome(str, Enum):
    cerrado = "cerrado"
    no_cerrado = "no_cerrado"
    pendiente = "pendiente"
    no_calificado = "no_calificado"



# --- INPUT ---

class CallAuditInput(BaseModel):
    transcript: str = Field(..., description="Transcripción completa de la llamada")
    closer_name: Optional[str] = Field(None, description="Nombre del closer")
    call_date: Optional[str] = Field(None, description="Fecha de la llamada (YYYY-MM-DD)")
    call_outcome: Optional[CallOutcome] = Field(None, description="Resultado de la llamada")
    duration_minutes: Optional[int] = Field(None, description="Duración en minutos")
    business_context: Optional[str] = Field(
        None,
        description="Contexto del negocio: estructura de la llamada, avatar, oferta."
    )


# --- OUTPUT COMPONENTS ---

class MetricaScore(BaseModel):
    score: int = Field(..., ge=1, le=10, description="Score de 1 a 10")
    justificacion: str = Field(..., description="Justificación con ejemplo concreto de la llamada")


class Metricas(BaseModel):
    # Apertura
    rapport: MetricaScore
    marco_conversacion: MetricaScore          # Marco + Estrella Polar

    # Discovery
    discovery_situacion_actual: MetricaScore
    discovery_dolor: MetricaScore             # Dolor + Cerrar puertas + Intentos pasados
    discovery_deseo: MetricaScore             # Deseo + Contraste + Consecuencia dolor futuro
    compromiso_y_urgencia: MetricaScore       # Compromiso + Porqué Ahora

    # Climax y Pitch
    climax: MetricaScore
    pitch_personalizado: MetricaScore
    comunidad_y_casos_exito: MetricaScore

    # Cierre
    garantia_y_check_temperatura: MetricaScore
    anclaje_precio: MetricaScore
    cierre_natural: MetricaScore
    manejo_objeciones: MetricaScore
    onboarding: MetricaScore

    # Transversal
    comunicacion_persuasiva: MetricaScore



# --- MAIN OUTPUT ---

class CallAuditOutput(BaseModel):
    # Metadata
    closer_name: Optional[str] = None
    call_date: Optional[str] = None
    call_outcome: Optional[str] = None
    duration_minutes: Optional[int] = None

    # Score total
    score_total: int = Field(..., ge=0, le=100, description="Score ponderado total sobre 100")

    # Métricas (15, alineadas con rúbrica)
    metricas: Metricas

    # Reporte narrativo
    resumen_ejecutivo: str = Field(..., description="3-5 oraciones: qué pasó y veredicto general")
    fortalezas: str = Field(..., description="2 a 4 fortalezas en texto con viñetas (•)")
    oportunidades_mejora: str = Field(..., description="2 a 4 oportunidades en texto con viñetas (•), cada una con punto, ejemplo concreto y cómo mejorarlo")
    objeciones_detectadas: str = Field(..., description="Objeciones en texto con viñetas (•), cada una con objeción, tipo, cómo la manejó, calidad y cita")
    proximas_acciones: str = Field(..., description="2-3 acciones concretas en texto con viñetas (•)")

    # Meta
    modelo_usado: str = Field(default="gpt-4.1-mini")
    procesado_en_segundos: Optional[float] = None
