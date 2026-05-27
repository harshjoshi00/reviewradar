export default function Logo({ size = 16 }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      style={{
        color: '#ffffff',
        display: 'block'
      }}
    >
      {/* Outer radar track */}
      <circle cx="12" cy="12" r="10" strokeDasharray="3 3" opacity="0.4" />
      
      {/* Inner radar track */}
      <circle cx="12" cy="12" r="6" strokeDasharray="2 2" opacity="0.7" />
      
      {/* Target center core */}
      <circle cx="12" cy="12" r="1.5" fill="currentColor" />
      
      {/* Radar scanning beam */}
      <path d="M12 2v10l7.5-3" />
    </svg>
  )
}
