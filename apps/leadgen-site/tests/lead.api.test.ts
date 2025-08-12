import handler from '../pages/api/lead'
import fs from 'fs'
import os from 'os'
import path from 'path'

function mockReqRes(body: any = {}) {
  const req: any = { method: 'POST', body, headers: {}, socket: { remoteAddress: '127.0.0.1' } }
  let statusCode = 200
  const res: any = {
    status(code: number) { statusCode = code; return this },
    json(payload: any) { this.payload = payload; this.statusCode = statusCode; return this },
  }
  return { req, res }
}

test('lead api writes and dedupes by email', async () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'leads-'))
  const leadsPath = path.join(tmp, 'leads.json')
  process.env.LEADS_FILE = leadsPath
  process.env.SMTP_HOST = '' // force no-op email

  const { req, res } = mockReqRes({ name: 'User', email: 'test@example.com', company: 'Co', phone: '123' })
  await handler(req as any, res as any)
  expect(res.statusCode || 200).toBe(200)

  const arr = JSON.parse(fs.readFileSync(leadsPath, 'utf-8'))
  expect(arr.length).toBe(1)

  const { req: req2, res: res2 } = mockReqRes({ name: 'User2', email: 'test@example.com', company: 'Co2' })
  await handler(req2 as any, res2 as any)
  const arr2 = JSON.parse(fs.readFileSync(leadsPath, 'utf-8'))
  expect(arr2.length).toBe(1)
})