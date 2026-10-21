=Analiza cuidadosamente la imagen proporcionada y determina si corresponde a un comprobante de transferencia bancaria digital o física (por ejemplo: comprobantes de BBVA, Banamex, Banorte, HSBC, Oxxo, SPEI u otros bancos reconocidos en México).

Un comprobante de transferencia bancaria debe cumplir con la mayoría de estas condiciones:
- Muestra claramente palabras o frases como: “Transferencia exitosa”, “Operación exitosa”, “Comprobante de transferencia”, “Depósito”, “Pago total”, “Folio de operación”, “Número de autorización”, “Cuenta origen”, “Cuenta destino”, “Banco”, “Concepto”.
- Contiene un monto en pesos mexicanos (ejemplo: $1,450.00 MXN).
- Incluye información del banco emisor o receptor (ej. BBVA, Banamex, Banorte, HSBC, Oxxo, SPEI, Santander, etc.).
- Presenta datos de origen y destino: nombre del beneficiario, cuenta CLABE, tarjeta o número de cuenta parcial/enmascarado.
- Tiene fecha y hora de la operación.

Rechaza como transferencia (retorna "false") si la imagen:
- Es un simple ticket de compra sin mención de transferencia.
- Solo contiene números o textos sin relación con bancos.
- Es un diseño, tabla, listado o documento genérico sin estructura de comprobante bancario.

Devuelve únicamente:
true → si la imagen es un comprobante de transferencia bancaria o depósito.
false → si la imagen NO es un comprobante de transferencia bancaria o depósito.
