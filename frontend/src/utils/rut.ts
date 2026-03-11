/**
 * Chilean RUT formatting and módulo 11 validation.
 */

/**
 * Normalize RUT to '12345678-9' format.
 * Strips dots and spaces, inserts dash before check digit if missing.
 */
export function normalizeRut(rut: string): string {
  if (!rut) return rut;
  // Remove dots and spaces
  let cleaned = rut.replace(/\./g, '').replace(/\s/g, '').trim().toUpperCase();
  // If no dash, insert before last char
  if (!cleaned.includes('-') && cleaned.length >= 2) {
    cleaned = cleaned.slice(0, -1) + '-' + cleaned.slice(-1);
  }
  return cleaned;
}

/**
 * Format RUT with dots for display: '12.345.678-9'
 */
export function formatRutDisplay(rut: string): string {
  const normalized = normalizeRut(rut);
  if (!normalized || !normalized.includes('-')) return normalized;

  const [body, dv] = normalized.split('-');
  const digits = body.replace(/\./g, '');

  let withDots = '';
  for (let i = 0; i < digits.length; i++) {
    if (i > 0 && (digits.length - i) % 3 === 0) {
      withDots += '.';
    }
    withDots += digits[i];
  }

  return `${withDots}-${dv}`;
}

/**
 * Validate Chilean RUT using módulo 11 algorithm.
 * Returns true if check digit is correct.
 */
export function validateRut(rut: string): boolean {
  const normalized = normalizeRut(rut);
  if (!normalized || !normalized.includes('-')) return false;

  const [body, dv] = normalized.split('-');
  const digits = body.replace(/\./g, '');

  if (!/^\d+$/.test(digits)) return false;

  let total = 0;
  let factor = 2;

  for (let i = digits.length - 1; i >= 0; i--) {
    total += parseInt(digits[i]) * factor;
    factor = factor < 7 ? factor + 1 : 2;
  }

  const remainder = total % 11;
  const computed = 11 - remainder;

  let computedDv: string;
  if (computed === 11) computedDv = '0';
  else if (computed === 10) computedDv = 'K';
  else computedDv = String(computed);

  return dv.toUpperCase() === computedDv;
}
