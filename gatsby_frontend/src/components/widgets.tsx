import React from 'react';
import { useAsyncDebounce } from 'react-table'
import Select from 'react-select'

const CardSelect = ({options, onChange, allSelectedCards, ...props}) => (
  <Select
    isMulti
    options={options.filter(option => !allSelectedCards.has(option))}
    onChange={onChange}
    {...props}
  />
)

export function GlobalCardFilter({
  preGlobalFilteredRows,
  globalFilter,
  setGlobalFilter,
}) {
  const count = preGlobalFilteredRows.length
  const [value, setValue] = React.useState(globalFilter)
  // const onChange = useAsyncDebounce(value => {
  //   setGlobalFilter(value || undefined)
  // }, 200)

  const [allSelectedCards, setAllSelectedCards] = React.useState(new Set())
  const options = React.useMemo(() => {
    return [
      { value: "ferocious", label: "ferocious" },
      { value: "relentless", label: "relentless" },
      { value: "cruel", label: "cruel" },
      { value: "scrappy", label: "scrappy" },
      { value: "strategic", label: "strategic" },
      { value: "rational", label: "rational" },
      { value: "stubborn", label: "stubborn" },
    ]
  }, [preGlobalFilteredRows])

  const onChange = (selectedItems) => {
    console.log("selectedItems", selectedItems)
    selectedItems.forEach(item => allSelectedCards.add("fukc"))
    setAllSelectedCards(allSelectedCards)
    console.log("allSelectedCards", allSelectedCards)
    setGlobalFilter(selectedItems.map(item => item.value) || undefined)
  }

  console.log("b allSelectedCards", allSelectedCards)
  return (
    <div>
      <CardSelect options={options} allSelectedCards={allSelectedCards} onChange={onChange} />
      <CardSelect options={options} allSelectedCards={allSelectedCards} onChange={onChange} />
    </div>
  )
}

// Define a default UI for filtering
export function GlobalFilter({
  preGlobalFilteredRows,
  globalFilter,
  setGlobalFilter,
}) {
  const count = preGlobalFilteredRows.length
  const [value, setValue] = React.useState(globalFilter)
  const onChange = useAsyncDebounce(value => {
    setGlobalFilter(value || undefined)
  }, 200)

  return (
    <span>
      Search:{' '}
      <input
        value={value || ""}
        onChange={e => {
          setValue(e.target.value);
          onChange(e.target.value);
        }}
        placeholder={`${count} records...`}
        style={{
          fontSize: '1.1rem',
          border: '0',
        }}
      />
    </span>
  )
}


// Define a default UI for filtering
export function DefaultColumnFilter({
  column: { filterValue, preFilteredRows, setFilter },
}) {
  const count = preFilteredRows.length

  return (
    <input
      value={filterValue || ''}
      onChange={e => {
        setFilter(e.target.value || undefined) // Set undefined to remove the filter entirely
      }}
      placeholder={`Search ${count} records...`}
    />
  )
}


// This is a custom filter UI for selecting
// a unique option from a list
export function CardFilter({
  column: { Header, filterValue, setFilter, preFilteredRows, id , ...rest},
  plugins,
  state,
  ...props
}) {
  // Calculate the options for filtering
  // using the preFilteredRows
  const options = React.useMemo(() => {
    return [
      { value: "ferocious", label: "ferocious" },
      { value: "relentless", label: "relentless" },
      { value: "cruel", label: "cruel" },
      { value: "scrappy", label: "scrappy" },
      { value: "strategic", label: "strategic" },
      { value: "rational", label: "rational" },
      { value: "stubborn", label: "stubborn" },
    ]
  }, [id, preFilteredRows])

  // const customThing = plugins.find(plugin => plugin.name == "customThing")
  // Render a multi-select box
  return (
    <Select
      isMulti
      options={options}
      onChange={item => {
        console.log("item", item)
        console.log("state", state)
        setFilter(item || undefined)
      }}
    />
  )
}

export function AdvantageFilter({
  column: { filterValue, setFilter, preFilteredRows, id },
}) {
  // Calculate the options for filtering
  // using the preFilteredRows
  const options = React.useMemo(() => {
    return [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]
  }, [id, preFilteredRows])

  // Render a multi-select box
  return (
    <select
      value={filterValue}
      onChange={e => {
        setFilter(e.target.value || undefined)
      }}
    >
      <option value="">All</option>
      {options.map((option, i) => (
        <option key={i} value={option}>
          {option}
        </option>
      ))}
    </select>
  )
}

// This is a custom filter UI that uses a
// slider to set the filter value between a column's
// min and max values
export function SliderColumnFilter({
  column: { filterValue, setFilter, preFilteredRows, id },
}) {
  // Calculate the min and max
  // using the preFilteredRows

  const [min, max] = React.useMemo(() => {
    let min = preFilteredRows.length ? preFilteredRows[0].values[id] : 0
    let max = preFilteredRows.length ? preFilteredRows[0].values[id] : 0
    preFilteredRows.forEach(row => {
      min = Math.min(row.values[id], min)
      max = Math.max(row.values[id], max)
    })
    return [min, max]
  }, [id, preFilteredRows])

  return (
    <>
      <input
        type="range"
        min={min}
        max={max}
        value={filterValue || min}
        onChange={e => {
          setFilter(parseInt(e.target.value, 10))
        }}
      />
      <button onClick={() => setFilter(undefined)}>Off</button>
    </>
  )
}
