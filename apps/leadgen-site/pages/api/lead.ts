import type { NextApiRequest, NextApiResponse } from 'next';
import fs from 'fs';
import path from 'path';
import { v4 as uuidv4 } from 'uuid';
import nodemailer from 'nodemailer';

function isValidEmail(email: string): boolean {
  return /.+@.+\..+/.test(email);
}

function getEnv(name: string, fallback?: string): string | undefined {
  return (process.env[name] as string) || fallback;
}

async function sendMail(to: string, subject: string, text: string) {
  const host = getEnv('SMTP_HOST');
  const port = parseInt(getEnv('SMTP_PORT', '587') || '587', 10);
  const user = getEnv('SMTP_USER');
  const pass = getEnv('SMTP_PASS');
  const from = getEnv('FROM_EMAIL') || getEnv('EMAIL_FROM') || '';
  if (!host || !user || !pass || !from) return; // graceful no-op
  const transporter = nodemailer.createTransport({ host, port, secure: false, auth: { user, pass } });
  await transporter.sendMail({ from, to, subject, text });
}

function getLeadsPath(): string {
  const override = process.env.LEADS_FILE;
  if (override) return override;
  const repoRoot = path.join(process.cwd(), '..', '..');
  return path.join(repoRoot, 'data', 'leads.json');
}

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }
  const { name, email, company, phone, message } = req.body || {};
  if (!name || !email || !company || !isValidEmail(email)) {
    res.status(400).json({ error: 'Invalid input' });
    return;
  }
  const record = {
    id: uuidv4(),
    name: String(name).slice(0, 200),
    email: String(email).slice(0, 200).toLowerCase(),
    company: String(company).slice(0, 200),
    phone: phone ? String(phone).slice(0, 50) : '',
    message: message ? String(message).slice(0, 2000) : '',
    created_at: new Date().toISOString(),
    source_ip: (req.headers['x-forwarded-for'] as string) || (req.socket as any).remoteAddress || '',
  };

  try {
    const leadsPath = getLeadsPath();
    let arr: any[] = [];
    if (fs.existsSync(leadsPath)) {
      try { arr = JSON.parse(fs.readFileSync(leadsPath, 'utf-8')); } catch { arr = []; }
    }
    // dedupe by email (keep first; if new email not present, append)
    const exists = arr.find((x: any) => (x.email || '').toLowerCase() === record.email);
    if (!exists) {
      arr.push(record);
      fs.mkdirSync(path.dirname(leadsPath), { recursive: true });
      fs.writeFileSync(leadsPath, JSON.stringify(arr, null, 2));
    }
  } catch (err) {
    // ignore FS errors in serverless
  }

  const toInternal = getEnv('TO_EMAIL') || getEnv('EMAIL_TO');
  const fromEmail = getEnv('FROM_EMAIL') || getEnv('EMAIL_FROM') || '';

  // receipt to lead
  try {
    await sendMail(record.email, 'Thanks — we received your request', `Hi ${record.name},\n\nWe received your request. We will reach out shortly.\n\n— A+ Enterprise LLC`);
  } catch {}
  // internal alert
  try {
    if (toInternal) {
      const summary = `New lead\nName: ${record.name}\nEmail: ${record.email}\nCompany: ${record.company}\nPhone: ${record.phone}\nMessage: ${record.message}`;
      await sendMail(toInternal, '[Lead] ' + record.name + ' <' + record.email + '>', summary);
    }
  } catch {}

  res.status(200).json({ ok: true });
}