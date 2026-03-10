"use client";

import Link from "next/link";
import { ArrowRight, Copy, Check, Github } from "lucide-react";
import { useState } from "react";

export default function HomePage() {
  const [copied, setCopied] = useState(false);

  const copyToClipboard = async () => {
    await navigator.clipboard.writeText("pip install typemap");
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section>
      <div className="grid grid-cols-10 lg:grid-cols-2">
        {/* Left column - content */}
        <div className="col-span-9 flex h-screen flex-col justify-between p-6 lg:col-span-1">

          {/* Middle section - hero */}
          <div className="flex flex-col gap-6 md:gap-8">
            <h3 className="text-5xl font-medium leading-tight md:max-w-lg md:text-6xl">
              Runtime type manipulation for Python
            </h3>

            <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
              <Link
                href="/docs"
                className="inline-flex items-center justify-center gap-2 px-6 py-2.5 border border-input rounded-md font-medium hover:bg-accent"
              >
                Get Started
                <ArrowRight className="h-4 w-4" />
              </Link>

              {/* Install Block */}
              <div className="flex items-center gap-2 rounded-md border border-border bg-background px-3 py-2">
                <code className="text-sm">pip install typemap</code>
                <button
                  onClick={copyToClipboard}
                  className="rounded-md p-1 hover:bg-accent"
                  aria-label="Copy command"
                >
                  {copied ? (
                    <Check className="h-4 w-4 text-green-600" />
                  ) : (
                    <Copy className="h-4 w-4 text-muted-foreground" />
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Bottom section - install and info */}
          <div className="flex flex-col gap-4">
            <div className="flex max-w-md flex-col gap-2 text-xs md:text-sm">
              <p className="text-muted-foreground">PEP 827 type manipulation library</p>
              <p className="text-xs text-muted-foreground">
                Evaluate, transform, and introspect types at runtime. Inspired by TypeScript.
              </p>
            </div>
          </div>
        </div>

        {/* Right column - visual */}
        <div className="col-span-1 h-screen min-h-0 overflow-hidden lg:block hidden border-l border-border/25">
          {/* EtheralShadow placeholder - gradient animation */}
          <div className="w-full h-full bg-gradient-to-br from-background via-accent/10 to-background animate-pulse" />
        </div>
      </div>
    </section>
  );
}
