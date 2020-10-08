import React from 'react';

import Container from 'react-bootstrap/Container'

import logo from './logo.svg';
import StatsTable from './StatsTable';
import Calc from './Calc';
import { expand } from './expand'
import { AdvantageFilter, CardFilter, SliderColumnFilter } from './widgets'
import all_data from '../results'

const expanded = expand()

// console.log("expanded", expanded[0])
// const expanded = [
//   {attacker_advantage: 1, attacker_hand: ["2"], defender_hand: ["3"], win_ratio: 4},
//   {attacker_advantage: 5, attacker_hand: ["6"], defender_hand: ["7"], win_ratio: 8},
// ]



function multiAnd(rows, id, filterValue) {
  console.log("rows", rows, "id", id, "filterValue", filterValue)
  return rows.filter(
    row => {
      const rowValue = row.values[id]
      return filterValue.every(({value}) => rowValue.includes(value))
    }
  )
}
// multiAnd.autoRemove = val => !val
console.log("expanded", expanded)

const ArrayCell = ({value}) => (
  value.some(item => (item === "")) ? "<empty>" : value.join(", ")
)


function App(props) {

  const columns = React.useMemo(
   () => [
      {
        Header: 'Attacker Advantage',
        accessor: 'attacker_advantage',
        Filter: AdvantageFilter,
        filter: 'includes',
      },
      {
        Header: 'Attacker Hand',
        accessor: 'attacker_hand',
        Filter: CardFilter,
        filter: multiAnd,
        Cell: ArrayCell,
      },
      {
        Header: 'Defender Hand',
        accessor: 'defender_hand',
        Filter: CardFilter,
        filter: multiAnd,
        Cell: ArrayCell,
      },
      {
        Header: 'Attacker Win Ratio',
        accessor: 'win_ratio',
      },
   ],
   []
  )
  // Convert back to memo?
  const data = React.useMemo(() => expanded, [])
  const [filteredData, setFilteredData] = React.useState(expanded)
  console.log("filteredData", filteredData)
  return (
    <Container>
      <Calc rawData={all_data} {...props} />
      {/*<StatsTable columns={columns} data={filteredData} />*/}
    </Container>
  );
}


export default App;
