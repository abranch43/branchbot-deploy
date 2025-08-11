import type { NextApiRequest, NextApiResponse } from 'next';
import fs from 'fs';
import path from 'path';
import { v4 as uuidv4 } from 'uuid';
import nodemailer from 'nodemailer';

function isValidEmail(email: string): boolean {
  return /.+@.+\..+/.test(email);
}

async function sendEmail(name: string, email: string, company?: string, message?: string) {
  const { SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, EMAIL_FROM, EMAIL_TO } = process.env as Record<string, string>;
  if (!SMTP_HOST || !SMTP_PORT || !SMTP_USER || !SMTP_PASS || !EMAIL_FROM || !EMAIL_TO) return;
  const transporter = nodemailer.createTransport({
    host: SMTP_HOST,
    port: parseInt(SMTP_PORT || '587', 10),
    secure: false,
    auth: { user: SMTP_USER, pass: SMTP_PASS },
  });
  const subject = `[Lead] ${name} <${email}>`;
  const text = `New lead\nName: ${name}\nEmail: ${email}\nCompany: ${company || ''}\nMessage: ${message || ''}`;
  await transporter.sendMail({ from: EMAIL_FROM, to: EMAIL_TO, subject, text });
}

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }
  const { name, email, company, message } = req.body || {};
  if (!name || !email || !isValidEmail(email)) {
    res.status(400).json({ error: 'Invalid input' });
    return;
  }
  const record = {
    id: uuidv4(),
    name: String(name).slice(0, 200),
    email: String(email).slice(0, 200),
    company: company ? String(company).slice(0, 200) : '',
    message: message ? String(message).slice(0, 2000) : '',
    created_at: new Date().toISOString(),
    source_ip: (req.headers['x-forwarded-for'] as string) || (req.socket as any).remoteAddress || '',
  };
  try {
    const repoRoot = path.join(process.cwd(), '..', '..');
    const leadsPath = path.join(repoRoot, 'data', 'leads.json');
    let arr: any[] = [];
    if (fs.existsSync(leadsPath)) {
      const current = fs.readFileSync(leadsPath, 'utf-8');
      try { arr = JSON.parse(current) } catch { arr = []; }
    }
    arr.push(record);
    fs.writeFileSync(leadsPath, JSON.stringify(arr, null, 2));
  } catch (err) {
  }
  try { await sendEmail(record.name, record.email, record.company, record.message); } catch {}
  res.status(200).json({ ok: true });
}