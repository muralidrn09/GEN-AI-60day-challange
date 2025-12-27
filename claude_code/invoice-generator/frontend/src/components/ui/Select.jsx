import { forwardRef } from 'react'
import clsx from 'clsx'

const Select = forwardRef(({ label, error, options, className, ...props }, ref) => {
  return (
    <div className="w-full">
      {label && <label className="label">{label}</label>}
      <select
        ref={ref}
        className={clsx('input', error && 'border-red-500', className)}
        {...props}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
    </div>
  )
})

Select.displayName = 'Select'

export default Select
