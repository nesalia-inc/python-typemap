"use client"

import { Copy, Check } from "lucide-react"
import { useState } from "react"

export function InstallBlock() {
  const [copied, setCopied] = useState(false)

  const copyToClipboard = async () => {
    await navigator.clipboard.writeText("pip install typemap")
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="flex w-full md:w-auto items-center gap-2 rounded-md border border-border bg-background px-3 py-2 shadow-xs dark:bg-input/30">
      <code className="flex-1 md:flex-none truncate text-sm text-foreground">
        pip install typemap
      </code>
      <button
        onClick={copyToClipboard}
        className="rounded-md p-1 transition-colors hover:bg-accent dark:hover:bg-input/50"
        aria-label="Copy command"
      >
        {copied ? (
          <Check className="h-4 w-4 text-green-600 dark:text-green-400" />
        ) : (
          <Copy className="h-4 w-4 text-muted-foreground" />
        )}
      </button>
    </div>
  )
}