// Reusable brand logo — shield with code symbol
// Compose from Lucide + custom SVG for the code mark inside.
export default function Logo({ size = 36 }: { size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 36 36"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-label="ReviewBot logo"
    >
      {/* Shield body */}
      <path
        d="M18 3L5 8.5V18C5 25.18 10.67 31.89 18 33.5C25.33 31.89 31 25.18 31 18V8.5L18 3Z"
        fill="url(#shield-gradient)"
      />
      {/* Code chevrons </>  */}
      <text
        x="18"
        y="22"
        textAnchor="middle"
        fontFamily="monospace"
        fontWeight="700"
        fontSize="11"
        fill="white"
        letterSpacing="-0.5"
      >
        {"</>"}
      </text>
      <defs>
        <linearGradient id="shield-gradient" x1="5" y1="3" x2="31" y2="33.5" gradientUnits="userSpaceOnUse">
          <stop stopColor="#DC143C" />
          <stop offset="1" stopColor="#A50E2B" />
        </linearGradient>
      </defs>
    </svg>
  );
}
