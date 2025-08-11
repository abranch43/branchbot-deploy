import React, { useState } from 'react';
import Link from 'next/link'

const Home: React.FC = () => {
  const [form, setForm] = useState({ name: '', email: '', company: '', phone: '', message: '' });
  const [status, setStatus] = useState<string | null>(null);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus('Sending...');
    try {
      const res = await fetch('/api/lead', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      if (res.ok) {
        setStatus('Thanks! We will reach out shortly.');
        setForm({ name: '', email: '', company: '', phone: '', message: '' });
      } else {
        setStatus('Failed to send. Please try again.');
      }
    } catch (err) {
      setStatus('Network error');
    }
  };

  const stripeUrl = process.env.NEXT_PUBLIC_STRIPE_PAYMENT_URL || process.env.STRIPE_PAYMENT_URL || process.env.NEXT_PUBLIC_STRIPE_CHECKOUT_URL || process.env.STRIPE_CHECKOUT_URL || '#';

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      <section className="text-center mb-10">
        <h1 className="text-4xl font-bold">A+ Enterprise LLC</h1>
        <p className="text-gray-600">SDVOSB • MBE • SDVE</p>
        <h2 className="text-2xl font-semibold mt-4">Reliable Janitorial, Facility Support, and IT Support</h2>
        <p className="mt-2">We deliver compliant, on-time services for government and enterprise clients.</p>
        <div className="mt-4">
          <a href={stripeUrl} target="_blank" rel="noopener" className="inline-block px-5 py-3 rounded bg-black text-white hover:bg-gray-800">Buy Now</a>
        </div>
      </section>

      <section className="grid md:grid-cols-3 gap-6 mb-10">
        <div>
          <h3 className="font-semibold mb-2">Services</h3>
          <ul className="list-disc pl-5 text-gray-700">
            <li>Janitorial and custodial services</li>
            <li>Facility operations and maintenance</li>
            <li>Helpdesk and IT support</li>
          </ul>
        </div>
        <div>
          <h3 className="font-semibold mb-2">Certifications</h3>
          <ul className="list-disc pl-5 text-gray-700">
            <li>Service-Disabled Veteran-Owned Small Business (SDVOSB)</li>
            <li>Minority Business Enterprise (MBE)</li>
            <li>Service-Disabled Veteran Enterprise (SDVE)</li>
          </ul>
        </div>
        <div>
          <h3 className="font-semibold mb-2">Proven Results</h3>
          <ul className="list-disc pl-5 text-gray-700">
            <li>On-time performance across federal and state contracts</li>
            <li>Clean audits and compliance track record</li>
            <li>Responsive 24/7 support</li>
          </ul>
        </div>
      </section>

      <section className="mb-10">
        <h3 className="text-xl font-semibold mb-3">Book a Call</h3>
        <form onSubmit={onSubmit} className="space-y-3 max-w-xl">
          <div>
            <label className="block text-sm">Name</label>
            <input required className="border rounded px-3 py-2 w-full" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} />
          </div>
          <div>
            <label className="block text-sm">Email</label>
            <input required type="email" className="border rounded px-3 py-2 w-full" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} />
          </div>
          <div>
            <label className="block text-sm">Company</label>
            <input required className="border rounded px-3 py-2 w-full" value={form.company} onChange={e => setForm({ ...form, company: e.target.value })} />
          </div>
          <div>
            <label className="block text-sm">Phone (optional)</label>
            <input className="border rounded px-3 py-2 w-full" value={form.phone} onChange={e => setForm({ ...form, phone: e.target.value })} />
          </div>
          <div>
            <label className="block text-sm">Message</label>
            <textarea className="border rounded px-3 py-2 w-full" value={form.message} onChange={e => setForm({ ...form, message: e.target.value })} />
          </div>
          <button type="submit" className="px-4 py-2 rounded bg-black text-white">Submit</button>
        </form>
        {status && <p className="mt-2 text-sm">{status}</p>}
      </section>

      <div className="text-center">
        <Link className="text-blue-600 underline" href="/thank-you">View Thank You Page</Link>
      </div>
    </div>
  );
};

export default Home;