"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import { ChevronLeft, ChevronRight, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { codeToHtml } from "shiki";

const examples = [
  {
    title: "KeyOf",
    description: "Get all field names as a tuple of Literals",
    href: "/docs/keyof",
    code: `from typemap import eval_typing
import typemap_extensions as tm

class User:
    name: str
    age: int
    email: str

# Get all field names at runtime!
keys = eval_typing(tm.KeyOf[User])
# Returns: tuple[Literal["name"], Literal["age"], Literal["email"]]`,
  },
  {
    title: "Pick",
    description: "Select specific fields from a type",
    href: "/docs/pick",
    code: `from typemap import eval_typing
import typemap_extensions as tm

class User:
    name: str
    age: int
    email: str
    password: str

# Pick only specific fields
PublicUser = eval_typing(tm.Pick[User, tuple["name", "email"]])
# Result: class with only name: str, email: str`,
  },
  {
    title: "Omit",
    description: "Exclude specific fields from a type",
    href: "/docs/omit",
    code: `from typemap import eval_typing
import typemap_extensions as tm

class User:
    name: str
    age: int
    email: str
    password: str
    hash: str

# Omit sensitive fields
SafeUser = eval_typing(tm.Omit[User, tuple["password", "hash"]])
# Result: class without password and hash`,
  },
  {
    title: "Partial",
    description: "Make all fields optional (non-recursive)",
    href: "/docs/partial",
    code: `from typemap import eval_typing
import typemap_extensions as tm

class User:
    name: str
    age: int
    email: str

# Make all fields optional
PartialUser = eval_typing(tm.Partial[User])
# Result: class with name: str | None, age: int | None, email: str | None`,
  },
  {
    title: "DeepPartial",
    description: "Make all fields recursively optional",
    href: "/docs/deep-partial",
    code: `from typemap import eval_typing
import typemap_extensions as tm

class Address:
    street: str
    city: str

class User:
    name: str
    address: Address

# Recursively make all nested fields optional
DeepUser = eval_typing(tm.DeepPartial[User])
# Result: address: Address | None with nested fields also optional`,
  },
];

export function CodeShowcase() {
  const [current, setCurrent] = useState(0);
  const [highlightedCode, setHighlightedCode] = useState<string>("");
  const [isAnimating, setIsAnimating] = useState(false);

  const changeExample = (newIndex: number) => {
    if (newIndex !== current) {
      setIsAnimating(true);
      setTimeout(() => {
        setCurrent(newIndex);
        setIsAnimating(false);
      }, 300);
    }
  };

  useEffect(() => {
    const highlight = async () => {
      const html = await codeToHtml(examples[current].code, {
        lang: "python",
        theme: "github-dark",
      });
      setHighlightedCode(html);
    };
    highlight();
  }, [current]);

  // Auto-rotate examples every 5 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      changeExample((current === examples.length - 1 ? 0 : current + 1));
    }, 5000);
    return () => clearInterval(interval);
  }, [current]);

  const prev = () => changeExample(current === 0 ? examples.length - 1 : current - 1);
  const next = () => changeExample(current === examples.length - 1 ? 0 : current + 1);

  return (
    <div className="flex h-full flex-col">
      {/* Header with title and description */}
      <div className={`border-b border-border/25 px-6 py-8 transition-opacity duration-300 ${isAnimating ? 'opacity-0' : 'opacity-100'}`}>
        <h3 className="text-3xl font-bold text-zinc-100">
          {examples[current].title}
        </h3>
        <p className="mt-2 text-base text-zinc-400">
          {examples[current].description}
        </p>
      </div>

      {/* Code block */}
      <div className={`flex-1 overflow-auto bg-background p-4 text-sm transition-opacity duration-300 ${isAnimating ? 'opacity-0' : 'opacity-100'}`}>
        <pre
          className="min-h-full bg-background [&_pre]:!bg-transparent"
          dangerouslySetInnerHTML={{ __html: highlightedCode }}
        />
      </div>

      {/* Footer with navigation */}
      <div className="flex items-center justify-between gap-2 border-t border-border/25 px-4 py-2">
        {/* See more button */}
        <Button variant="outline" asChild>
          <Link href={examples[current].href}>
            See more
            <ArrowRight className="ml-1.5 h-4 w-4" />
          </Link>
        </Button>

        {/* Navigation buttons */}
        <div className="flex items-center gap-2">
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="outline"
                size="icon"
                onClick={prev}
                className="h-8 w-8 border-zinc-700 text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200"
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="top">Previous example</TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="outline"
                size="icon"
                onClick={next}
                className="h-8 w-8 border-zinc-700 text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200"
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="top">Next example</TooltipContent>
          </Tooltip>
        </div>
      </div>
    </div>
  );
}
