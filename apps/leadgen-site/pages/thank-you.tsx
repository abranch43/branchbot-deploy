export default function ThankYou() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-16">
      <h1 className="text-3xl font-semibold mb-4">Thank you!</h1>
      <p className="mb-6">Your order is received. Next steps:
      </p>
      <ol className="list-decimal pl-6 space-y-2">
        <li>Check your email for a receipt and onboarding form.</li>
        <li>Prepare access details (domains, SMTP, API keys) for setup.</li>
        <li>Book your setup call below.</li>
      </ol>
      <div className="mt-8 p-4 border rounded">
        <h2 className="text-xl font-semibold mb-2">Schedule your setup call</h2>
        <a className="inline-block px-4 py-2 bg-black text-white rounded hover:bg-gray-800" href="#" target="_blank" rel="noreferrer">Open Calendar</a>
      </div>
    </div>
  )
}