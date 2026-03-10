"use client";

import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { InstallBlock } from "@/components/install-block";
import { CodeShowcase } from "@/components/code-showcase";

export default function HomePage() {
  return (
    <section className="flex flex-1">
      <div className="grid grid-cols-1 lg:grid-cols-2 flex-1">
        {/* Left column - content */}
        <div className="flex flex-1 flex-col p-6 md:p-8 lg:p-6">
          {/* Hero section - centered */}
          <div className="flex flex-1 flex-col justify-center gap-6 md:gap-8">
            {/* Top badge */}
            <div className="flex flex-col gap-4">
              <Link
                href="https://peps.python.org/pep-0827/"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex w-fit items-center gap-2 rounded-full border border-zinc-700 bg-zinc-900/50 px-3 py-1 text-xs font-medium text-zinc-300 hover:bg-zinc-800 transition-colors"
              >
                <span className="relative flex h-2 w-2">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500"></span>
                </span>
                PEP 827 Draft
              </Link>

              <h3 className="text-4xl font-medium leading-tight md:text-5xl lg:text-5xl xl:text-6xl">
                Runtime type manipulation for Python
              </h3>
            </div>

            <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
              <Button variant="outline" asChild className="h-10">
                <Link href="/docs">
                  Get Started
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>

              <InstallBlock />
            </div>
          </div>

          {/* Bottom section - install and info */}
          <div className="flex flex-col gap-4">
            <div className="flex max-w-md flex-col gap-2 text-xs md:text-sm">
              <p className="text-muted-foreground">
                PEP 827 type manipulation library
              </p>
              <p className="text-xs text-muted-foreground">
                Evaluate, transform, and introspect types at runtime. Inspired
                by TypeScript.
              </p>
            </div>
          </div>
        </div>

        {/* Right column - code showcase */}
        <div className="hidden md:flex flex-1 min-h-0 overflow-hidden lg:block border-t lg:border-t-0 lg:border-l border-border pb-4">
          <CodeShowcase />
        </div>
      </div>
    </section>
  );
}
