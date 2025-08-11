import React, { useState } from 'react';

const Home: React.FC = () => {
  const [form, setForm] = useState({ name: '', email: '', company: '', message: '' });
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
        setForm({ name: '', email: '', company: '', message: '' });
      } else {
        setStatus('Failed to send. Please try again.');
      }
    } catch (err) {
      setStatus('Network error');
    }
  };

  const stripeUrl = process.env.NEXT_PUBLIC_STRIPE_CHECKOUT_URL || process.env.STRIPE_CHECKOUT_URL || '#';

  return (
    <main style={{ fontFamily: 'system-ui, sans-serif', maxWidth: 900, margin: '0 auto', padding: '2rem' }}>
      <section style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <h1>A+ Enterprise LLC</h1>
        <p>SDVOSB • MBE • SDVE</p>
        <h2>Reliable Janitorial, Facility Support, and IT Support</h2>
        <p>We deliver compliant, on-time services for government and enterprise clients.</p>
        <div style={{ marginTop: '1rem' }}>
          <a href={stripeUrl} target="_blank" rel="noopener" style={{ padding: '0.75rem 1.25rem', background: '#111', color: '#fff', borderRadius: 8 }}>Buy Now</a>
        </div>
      </section>

      <section>
        <h3>Services</h3>
        <ul>
          <li>Janitorial and custodial services</li>
          <li>Facility operations and maintenance</li>
          <li>Helpdesk and IT support</li>
        </ul>
      </section>

      <section>
        <h3>Certifications</h3>
        <ul>
          <li>Service-Disabled Veteran-Owned Small Business (SDVOSB)</li>
          <li>Minority Business Enterprise (MBE)</li>
          <li>Service-Disabled Veteran Enterprise (SDVE)</li>
        </ul>
      </section>

      <section>
        <h3>Proven Results</h3>
        <ul>
          <li>On-time performance across federal and state contracts</li>
          <li>Clean audits and compliance track record</li>
          <li>Responsive 24/7 support</li>
        </ul>
      </section>

      <section>
        <h3>Book a Call</h3>
        <form onSubmit={onSubmit}>
          <div>
            <label>Name<br/>
              <input required value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} />
            </label>
          </div>
          <div>
            <label>Email<br/>
              <input required type="email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} />
            </label>
          </div>
          <div>
            <label>Company<br/>
              <input value={form.company} onChange={e => setForm({ ...form, company: e.target.value })} />
            </label>
          </div>
          <div>
            <label>Message<br/>
              <textarea value={form.message} onChange={e => setForm({ ...form, message: e.target.value })} />
            </label>
          </div>
          <button type="submit">Submit</button>
        </form>
        {status && <p>{status}</p>}
      </section>

      <footer style={{ marginTop: '3rem', textAlign: 'center', color: '#666' }}>
        <small>© {new Date().getFullYear()} A+ Enterprise LLC</small>
      </footer>
    </main>
  );
};

export default Home;