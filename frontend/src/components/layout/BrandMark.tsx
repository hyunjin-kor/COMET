import { useId } from 'react';

type BrandMarkProps = {
  className?: string;
};

export default function BrandMark({ className = 'h-12 w-12' }: BrandMarkProps) {
  const gradientKey = useId().replace(/:/g, '');
  const bgId = `cp-bg-${gradientKey}`;
  const frameId = `cp-frame-${gradientKey}`;
  const signalId = `cp-signal-${gradientKey}`;

  return (
    <svg viewBox="0 0 512 512" fill="none" aria-hidden="true" className={className}>
      <defs>
        <linearGradient id={bgId} x1="86" y1="64" x2="426" y2="448" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#171c24" />
          <stop offset="100%" stopColor="#2a313d" />
        </linearGradient>
        <linearGradient id={frameId} x1="192" y1="134" x2="320" y2="362" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#f1f6ff" />
          <stop offset="100%" stopColor="#a1b1c8" />
        </linearGradient>
        <linearGradient id={signalId} x1="154" y1="338" x2="358" y2="208" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#3ac8ff" />
          <stop offset="100%" stopColor="#49e0c1" />
        </linearGradient>
      </defs>

      <rect x="40" y="40" width="432" height="432" rx="110" fill={`url(#${bgId})`} />
      <rect x="54" y="54" width="404" height="404" rx="96" stroke="#3c4659" strokeWidth="8" />
      <g opacity="0.16" stroke="#d8e1ef" strokeWidth="4" strokeLinecap="round">
        <path d="M156 166H356" />
        <path d="M156 214H356" />
        <path d="M156 262H356" />
        <path d="M156 310H356" />
        <path d="M156 358H356" />
        <path d="M192 142V382" />
        <path d="M256 142V382" />
        <path d="M320 142V382" />
      </g>
      <path
        d="M214 132 H298 L320 176 V308
           C320 338 296 362 266 362
           H246
           C216 362 192 338 192 308
           V176
           Z"
        fill="none"
        stroke={`url(#${frameId})`}
        strokeWidth="20"
        strokeLinejoin="round"
      />
      <path
        d="M204 232 H308 V298
           C308 317 293 332 274 332
           H238
           C219 332 204 317 204 298
           Z"
        fill="#243240"
      />
      <g fill="#e7eef8">
        <circle cx="228" cy="256" r="12" />
        <circle cx="256" cy="240" r="12" />
        <circle cx="284" cy="256" r="12" />
        <circle cx="240" cy="286" r="12" />
        <circle cx="268" cy="286" r="12" />
      </g>
      <path
        d="M154 338
           C194 320 226 304 258 286
           C292 266 324 240 358 208"
        fill="none"
        stroke={`url(#${signalId})`}
        strokeWidth="18"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <g fill="#171c24" stroke="#49dec6" strokeWidth="7">
        <circle cx="154" cy="338" r="11" />
        <circle cx="258" cy="286" r="11" />
        <circle cx="358" cy="208" r="11" />
      </g>
    </svg>
  );
}
