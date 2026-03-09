import Link from "next/link";

export default function HomePage() {
  return (
    <div className="flex flex-col justify-center text-center flex-1">
      <h1 className="text-4xl font-bold mb-4">typemap</h1>
      <p className="text-lg text-gray-600 mb-8">
        PEP 827 type manipulation library for Python 3.14+
      </p>
      <p className="mb-8">
        A runtime type evaluation library that implements the type manipulation operators from PEP 827.
      </p>
      <div className="flex gap-4 justify-center">
        <Link
          href="/docs"
          className="px-6 py-2 bg-black text-white rounded-lg font-medium hover:bg-gray-800"
        >
          Get Started
        </Link>
        <Link
          href="https://github.com/nesalia-inc/python-typemap"
          className="px-6 py-2 border border-gray-300 rounded-lg font-medium hover:bg-gray-50"
        >
          GitHub
        </Link>
      </div>
    </div>
  );
}
