"use client";

import Link from "next/link";
import { ArrowRight, Copy, Check } from "lucide-react";
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
      <div className="grid grid-cols-1 lg:grid-cols-2 min-h-[calc(100vh-4rem)]">
        {/* Left column - content */}
        <div className="flex flex-col justify-center p-6 lg:p-12">
          {/* Middle section - hero */}
          <div className="flex flex-col gap-6">
            <h1 className="text-4xl md:text-6xl font-bold tracking-tight">
              Runtime type manipulation for Python
            </h1>

            <p className="text-lg text-muted-foreground max-w-lg">
              Evaluate, transform, and introspect types at runtime.
              Inspired by TypeScript and built for Python 3.14+.
            </p>

            <div className="flex flex-col sm:flex-row gap-3">
              <Link
                href="/docs"
                className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-foreground text-background rounded-lg font-medium hover:opacity-90"
              >
                Get Started
                <ArrowRight className="h-4 w-4" />
              </Link>

              <Link
                href="https://github.com/nesalia-inc/python-typemap"
                target="_blank"
                className="inline-flex items-center justify-center px-6 py-3 border border-border rounded-lg font-medium hover:bg-accent"
              >
                View on GitHub
              </Link>
            </div>

            <div className="flex flex-col gap-2 pt-4">
              <p className="text-sm text-muted-foreground">Install via pip</p>
              <button
                onClick={copyToClipboard}
                className="flex items-center gap-2 rounded-md border border-border bg-background px-4 py-2 font-mono text-sm hover:bg-accent w-fit"
              >
                pip install typemap
                {copied ? (
                  <Check className="h-4 w-4 text-green-600" />
                ) : (
                  <Copy className="h-4 w-4 text-muted-foreground" />
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Right column - visual */}
        <div className="hidden lg:flex items-center justify-center bg-gradient-to-br from-background via-accent/10 to-background border-l border-border">
          <div className="flex flex-col gap-4 p-8">
            <pre className="text-sm bg-muted p-4 rounded-lg overflow-x-auto">
{`from typemap import eval_typing
import typemap_extensions as tm

class User:
    name: str
    age: int
    email: str

# Get all field names!
keys = eval_typing(tm.KeyOf[User])
# tuple[Literal["name"], Literal["age"], Literal["email"]]`}
            </pre>
            <p className="text-sm text-muted-foreground text-center">
              Type-level introspection at runtime
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
