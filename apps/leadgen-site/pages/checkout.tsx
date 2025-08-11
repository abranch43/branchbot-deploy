import { useEffect } from 'react'

export default function Checkout() {
  useEffect(() => {
    const url = process.env.NEXT_PUBLIC_STRIPE_PAYMENT_URL || process.env.STRIPE_PAYMENT_URL || process.env.NEXT_PUBLIC_STRIPE_CHECKOUT_URL || process.env.STRIPE_CHECKOUT_URL
    if (url) {
      window.location.href = url as string
    }
  }, [])
  return (
    <div className="max-w-xl mx-auto px-4 py-16">
      <h1 className="text-2xl font-semibold mb-2">Redirecting to Checkout…</h1>
      <p>If you are not redirected automatically, <a className="text-blue-600 underline" href={(process.env.NEXT_PUBLIC_STRIPE_PAYMENT_URL as string) || '#'}>click here</a>.</p>
    </div>
  )
}