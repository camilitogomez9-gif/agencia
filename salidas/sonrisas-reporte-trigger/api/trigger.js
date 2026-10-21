export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const response = await fetch('https://[TU-INSTANCIA-N8N]/webhook/reporte_facturacion', {
    method: 'POST',
    headers: { 'h': 'fohfiw-jojqYb-ruqno3' },
  });

  if (!response.ok) {
    return res.status(response.status).json({ status: 'error', message: 'No se pudo conectar con n8n' });
  }

  const data = await response.json().catch(() => ({}));
  return res.status(200).json(data);
}
