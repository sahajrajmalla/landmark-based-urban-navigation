
import './globals.css'
import { Inter } from 'next/font/google'



import 'leaflet/dist/leaflet.css';
import Head from 'next/head';


const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'DnD Algorithm',
  description: 'Lets get hasshhh',
  favicon: '/favicon.svg'
}


export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
      {/* <link rel="icon" href="/favicon.svg" sizes="any" /> */}
      </head>
      <body className={inter.className}>{children}</body>
    </html>
  )
}
