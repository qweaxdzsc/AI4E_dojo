import React from "react"
import { createRoot } from "react-dom/client"
import App from "./App.jsx"
import "./styles.css"

window.__QODER_CANVAS_RUNTIME__ = { mode: "design" }

const originalFetch = window.fetch?.bind(window)
const originalOpen = window.open?.bind(window)
const originalXhrOpen = XMLHttpRequest.prototype.open
const originalXhrSend = XMLHttpRequest.prototype.send
const blockedResponse = () => new Response(JSON.stringify({ blocked: true, runtime: "design" }), {
  status: 200,
  headers: { "content-type": "application/json" },
})

function getRequestUrl(input) {
  if (typeof Request !== "undefined" && input instanceof Request) return input.url
  if (input instanceof URL) return input.href
  return String(input)
}

function getRequestMethod(input, init) {
  if (init?.method) return String(init.method).toUpperCase()
  if (typeof Request !== "undefined" && input instanceof Request) return input.method.toUpperCase()
  return "GET"
}

function allowsDesignRead(url, method) {
  if (method !== "GET" && method !== "HEAD") return false
  try {
    const parsed = new URL(url, window.location.href)
    return parsed.origin === window.location.origin
  } catch {
    return false
  }
}

if (originalFetch) {
  window.fetch = (input, init) => {
    const url = getRequestUrl(input)
    const method = getRequestMethod(input, init)
    if (!allowsDesignRead(url, method)) return Promise.resolve(blockedResponse())
    return originalFetch(input, init)
  }
}

XMLHttpRequest.prototype.open = function(method, url, ...rest) {
  this.__qoderCanvasBlocked = !allowsDesignRead(String(url), String(method).toUpperCase())
  return originalXhrOpen.call(this, method, this.__qoderCanvasBlocked ? window.location.href : url, ...rest)
}

XMLHttpRequest.prototype.send = function(body) {
  if (!this.__qoderCanvasBlocked) return originalXhrSend.call(this, body)
  setTimeout(() => {
    this.dispatchEvent(new Event("loadend"))
  }, 0)
}

if (navigator.sendBeacon) {
  navigator.sendBeacon = () => false
}

function patchStorage(storage) {
  if (!storage) return
  for (const method of ["setItem", "removeItem", "clear"]) {
    try {
      Object.defineProperty(storage, method, {
        configurable: true,
        value: () => undefined,
      })
    } catch {
    }
  }
}

patchStorage(window.localStorage)
patchStorage(window.sessionStorage)

if (originalOpen) {
  window.open = () => null
}

window.addEventListener("submit", (event) => {
  event.preventDefault()
}, true)

window.addEventListener("click", (event) => {
  const target = event.target instanceof Element ? event.target.closest("a[href]") : null
  if (!target) return
  const href = target.getAttribute("href")
  if (!href || href.startsWith("#")) return
  event.preventDefault()
}, true)

createRoot(document.getElementById("root")).render(
  <React.StrictMode data-qoder-id="qel-react-strictmode-768d8241" data-qoder-source="{&quot;qoderId&quot;:&quot;qel-react-strictmode-768d8241&quot;,&quot;filePath&quot;:&quot;frontend/src/qoder-design-runtime.jsx&quot;,&quot;componentName&quot;:&quot;Unknown&quot;,&quot;elementRole&quot;:&quot;react-strictmode&quot;,&quot;loc&quot;:{&quot;line&quot;:97,&quot;column&quot;:3}}">
    <App  data-qoder-id="qel-app-3dbd7413" data-qoder-source="{&quot;qoderId&quot;:&quot;qel-app-3dbd7413&quot;,&quot;filePath&quot;:&quot;frontend/src/qoder-design-runtime.jsx&quot;,&quot;componentName&quot;:&quot;Unknown&quot;,&quot;elementRole&quot;:&quot;app&quot;,&quot;loc&quot;:{&quot;line&quot;:98,&quot;column&quot;:5}}"/>
  </React.StrictMode>,
)
