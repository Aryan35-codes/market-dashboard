import React from "react";

export default function Logo({ className = "h-8 w-8" }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 100 100"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      {/* Abstract G Shape */}
      <path
        d="M80 50C80 66.5685 66.5685 80 50 80C33.4315 80 20 66.5685 20 50C20 33.4315 33.4315 20 50 20C55.4545 20 60.5455 21.4545 65 24"
        stroke="currentColor"
        strokeWidth="8"
        strokeLinecap="round"
      />
      {/* Chart Line / Upward Arrow */}
      <path
        d="M45 55L55 45L65 55L85 30"
        stroke="currentColor"
        strokeWidth="8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M75 30H85V40"
        stroke="currentColor"
        strokeWidth="8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {/* Horizontal Bar of G */}
      <path
        d="M50 50H75"
        stroke="currentColor"
        strokeWidth="8"
        strokeLinecap="round"
      />
    </svg>
  );
}
