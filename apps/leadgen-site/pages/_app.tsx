import type { AppProps } from 'next/app'
import Link from 'next/link'
import '../styles/globals.css'

export default function MyApp({ Component, pageProps }: AppProps) {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="w-full border-b">
        <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link href="/" className="font-semibold">A+ Enterprise LLC</Link>
          <Link href="/checkout" className="px-3 py-2 rounded-md bg-black text-white hover:bg-gray-800 text-sm">Get Automation Setup – $897</Link>
        </div>
      </header>
      <main className="flex-1">
        <Component {...pageProps} />
      </main>
      <footer className="border-t text-center text-gray-500 text-sm py-4">© {new Date().getFullYear()} A+ Enterprise LLC</footer>
    </div>
  )
}