import React from 'react';
import signexLogoImg from '../assets/signex_logo.png';

export default function SignexLogo({ className = "h-8", showSubtitle = true, theme = "dark" }) {
  return (
    <div className={`flex items-center select-none ${className}`}>
      {/* Exact User Uploaded Logo Image from src/assets/ */}
      <div className="rounded-md overflow-hidden flex items-center justify-center">
        <img
          src={signexLogoImg}
          alt="SIGNEX - Signal Extraction & Analysis Engine"
          className="h-8 sm:h-9 w-auto object-contain max-w-full"
        />
      </div>
    </div>
  );
}
