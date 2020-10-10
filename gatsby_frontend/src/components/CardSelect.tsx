import React from "react"

import Select from "react-select"

const CardSelect = ({
  options,
  onChange,
  optionsAreDisabled,
  availableCards,
  ...props
}) => {
  const filtered = options.filter(({ value }) => availableCards.includes(value))
  return (
    <Select
      isMulti
      options={filtered}
      onChange={onChange}
      isOptionDisabled={option => optionsAreDisabled}
      {...props}
    />
  )
}

export default CardSelect
