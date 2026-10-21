// Telegram Trigger -> shape base para la cadena de resolucion de CRM.
// NO inventa ids de GHL: contact_id y opportunity_id los resuelve la cadena "GHL: ..." aguas abajo.
// La unica diferencia con produccion (WhatsApp/GHL) es el canal: aca la identidad del lead
// se ancla al chat de Telegram via un email deterministico.
return $input.all().map(item => {
  const j    = item.json || {};
  const msg  = j.message || j;
  const chat = msg.chat || {};
  const from = msg.from || {};

  const chatId = String(chat.id ?? from.id ?? '');
  if (!chatId) throw new Error('Update de Telegram sin chat.id');

  let message_type     = 'text';
  let message_text     = msg.text || msg.caption || '';
  let telegram_file_id = '';

  if (msg.voice || msg.audio) {
    message_type = 'audio';
    telegram_file_id = (msg.voice || msg.audio).file_id || '';
  } else if (Array.isArray(msg.photo) && msg.photo.length) {
    message_type = 'image';
    telegram_file_id = msg.photo[msg.photo.length - 1].file_id || '';
  } else if (!message_text) {
    // sticker / gif / documento / video / ubicacion / contacto: no los podemos leer,
    // pero NO deben tirar la ejecucion. El agente responde con naturalidad.
    message_type = 'text';
    message_text = '(el lead mando un sticker o archivo que no puedo abrir)';
  }

  // /start de Telegram = "el lead abrio el chat" -> equivale a un saludo, no a un comando.
  const raw = String(message_text).trim().toLowerCase();
  if (raw === '/start') message_text = 'hola';

  const RESET = ['/b', '/borrar', '/reset', '/clear'];
  const is_command = RESET.includes(raw);

  const first_name = from.first_name || chat.first_name || '';
  const last_name  = from.last_name  || chat.last_name  || '';
  const full_name  = [first_name, last_name].filter(Boolean).join(' ') || ('Telegram ' + chatId);

  return {
    json: {
      source: 'telegram',
      channel: 'telegram',
      telegram_chat_id: chatId,
      session_key: 'tg_' + chatId,
      first_name,
      last_name,
      full_name,
      // Email deterministico: es la llave de dedup del upsert de GHL (Telegram no da telefono).
      email_sintetico: 'tg-' + chatId + '@telegram.[TU-DOMINIO]',
      message_type,
      message_text,
      media_url: '',
      media_type: '',
      telegram_file_id,
      is_command,
    },
  };
});
