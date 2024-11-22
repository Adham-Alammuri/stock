import React from 'react';
import { Check } from 'lucide-react';

const Checkbox = ({ 
  label, 
  checked, 
  onChange,
  className = ''
}) => {
  return (
    <label className="inline-flex items-center gap-2 cursor-pointer">
      <div 
        onClick={() => onChange(!checked)}
        className={`
          w-4 h-4 flex items-center justify-center
          border rounded transition-colors
          ${checked ? 'bg-blue-500 border-blue-500' : 'border-gray-300 bg-white'}
          ${className}
        `}
      >
        {checked && <Check className="w-3 h-3 text-white" />}
      </div>
      <span className="text-sm text-gray-700">{label}</span>
    </label>
  );
};

export default Checkbox;