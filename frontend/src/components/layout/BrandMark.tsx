type BrandMarkProps = {
  className?: string;
};

export default function BrandMark({ className = 'h-12 w-12' }: BrandMarkProps) {
  return (
    <svg viewBox="0 0 160 160" fill="none" aria-hidden="true" className={className}>
      <defs>
        <linearGradient id="cp-bg" x1="80" y1="14" x2="80" y2="146" gradientUnits="userSpaceOnUse">
          <stop stopColor="#5CC1FF" />
          <stop offset="1" stopColor="#2676DB" />
        </linearGradient>
        <radialGradient id="cp-shine" cx="30%" cy="22%" r="36%">
          <stop stopColor="#FFFFFF" stopOpacity="0.22" />
          <stop offset="1" stopColor="#FFFFFF" stopOpacity="0" />
        </radialGradient>
        <linearGradient id="cp-core" x1="80" y1="40" x2="80" y2="124" gradientUnits="userSpaceOnUse">
          <stop stopColor="#17365E" />
          <stop offset="1" stopColor="#0D2445" />
        </linearGradient>
      </defs>

      <rect x="14" y="14" width="132" height="132" rx="36" fill="url(#cp-bg)" />
      <rect x="14.75" y="14.75" width="130.5" height="130.5" rx="35.25" stroke="#FFFFFF" strokeOpacity="0.36" strokeWidth="1.5" />
      <circle cx="52" cy="44" r="28" fill="url(#cp-shine)" />

      <path
        d="M80 42 106 58V102L80 118 54 102V58L80 42Z"
        fill="url(#cp-core)"
        stroke="#E8F5FF"
        strokeOpacity="0.92"
        strokeWidth="4"
        strokeLinejoin="round"
      />
      <circle cx="68" cy="74" r="7" fill="#A5F2E0" />
      <circle cx="92" cy="74" r="7" fill="#A5F2E0" />
      <circle cx="80" cy="92" r="7" fill="#A5F2E0" />

      <path d="M42 106 62 92 80 98 108 68" stroke="#FFFFFF" strokeWidth="13" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M120 58 100 62 108 80Z" fill="#FFD66B" />
    </svg>
  );
}
