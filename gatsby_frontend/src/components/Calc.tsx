// TODO: Add "swap sides" button to reverse attacker/defender
// TODO: If number is small enough, show possible "outs" for disadvantaged attacks

import React from 'react'

import Select from 'react-select'
import Button from 'react-bootstrap/Button'
import Form from 'react-bootstrap/Form'
import Col from 'react-bootstrap/Col'
import Row from 'react-bootstrap/Row'
import { navigate } from "gatsby"

import isEqual from 'lodash/isEqual'
import range from 'lodash/range'
import sum from 'lodash/sum'
import round from 'lodash/round'
import { InlineMath, BlockMath } from 'react-katex';

const calcAdvantage = (selected_ship_option, selected_card_options) => {
  const cardsWithAdvantage = selected_card_options.filter(
    (option) => typeof option.advantage !== 'undefined'
  )
 return sum(cardsWithAdvantage.map((option) => option.advantage))
}

const Results = ({ attacker_ship, defender_ship, attacker_hand, defender_hand, attackerWinRatio }) => {
  const rawAdvantage = attacker_ship.value - defender_ship.value
  const effectiveAdvantage = (
     - calcAdvantage(defender_ship, defender_hand)
  )
  const rawAdvantageHelp = (
    '"Raw advantage" is simply the attacker ship die minus the defender ship ' +
    'die. So, lower numbers are better for the attacker'
  )
  const effectiveAdvantageHelp = (
    '"Effective advantage" is (attacker_ship_die + advantage_from_cards) - ' +
    '(defender_ship_die + advantage_from_cards). So, lower numbers are better for the attacker'
  )

  let resultsCategory
  if (attackerWinRatio > .7) {
    resultsCategory = "results-good"
  } else if (attackerWinRatio > .5) {
    resultsCategory = "results-medium"
  } else {
    resultsCategory = "results-bad"
  }

  return (
    <>
      <p title={rawAdvantageHelp}>
        Raw combat advantage:<br />
        <BlockMath>{`${attacker_ship.value} - ${defender_ship.value} = ${rawAdvantage}`}</BlockMath>
      </p>
      <p title={effectiveAdvantageHelp}>
        Effective combat advantage:<br />
        <BlockMath>{`(${attacker_ship.value} + ${calcAdvantage(attacker_ship, attacker_hand)}) - (${defender_ship.value} + ${calcAdvantage(defender_ship, defender_hand)}) = ${effectiveAdvantage}`}</BlockMath>
      </p>
      <hr />
      <p className={`results ${resultsCategory}`}>
        Attacker Win Ratio:<br />
        <BlockMath>{`${attackerWinRatio * 100}\\%`}</BlockMath>
      </p>
    </>
  )
}
const CardSelect = ({options, onChange, optionsAreDisabled, availableCards, ...props}) => {
    const filtered = options.filter(({value}) => availableCards.includes(value))
    return (
      <Select
        isMulti
        options={filtered}
        onChange={onChange}
        isOptionDisabled={(option) => optionsAreDisabled}
        {...props}
      />
    )
}

const buildOptions = (start, end) => (
  range(start, end + 1).map(
    (item) => ({ value: item, label: item })
  )
)

function formatRatio(ratio) {
  return `${round(ratio * 100, 2)}%`
}


function genExplanation(selectedAttackerShip, attackerHand, selectedDefenderShip, defenderHand, rawData) {
  const attackerAdvantageStr = JSON.stringify(selectedAttackerShip.value - selectedDefenderShip.value)
  const attackerBaseStr = `Attacker ${selectedAttackerShip.value}`
  const attackerHandStr = attackerHand.length ? ` (${attackerHand.join(", ")})` : ""
  const defenderBaseStr = ` vs. Defender ${selectedDefenderShip.value}`
  const defenderHandStr = defenderHand.length ? ` (${defenderHand.join(", ")})` : ""
  
  let attackerWinRatio;
  const explanation = `${attackerBaseStr}${attackerHandStr}${defenderBaseStr}${defenderHandStr}`
  if (selectedAttackerShip) {
    attackerWinRatio = rawData[attackerAdvantageStr][attackerHand.join("|")][defenderHand.join("|")]
  } else {
    attackerWinRatio = NaN
  }

  return [explanation, attackerWinRatio]
}

const HandExplanation = ({ hand }) => {
  if (hand.length) {
    return (
      <>
      <hr />
      <ul>
        {
          hand.map(option => (
            <li>
              <b>{option.label}</b>: {option.description}
            </li>
          ))
        }
      </ul>
      </>
    )
  }
  return null
}


export const Calc = ({ rawData, location }) => {
  const updateSearchParams = (paramName, paramValue) => {
    console.log("updateSearchParams", searchParams)
    if (paramValue == null) {
      searchParams.delete(paramName)
    }
    else if (paramValue.length) {
      searchParams.set(paramName, paramValue.map(option => option.value).sort().join(","))
    } else {
      searchParams.set(paramName, paramValue.value)
    }
    
  }

  const searchParamsToUrl = (searchParams) => {
    const url_ = `${location.pathname}?${searchParams.toString()}`
    searchParams.forEach(
      (value, key) => {
        if (value === "undefined") {
          console.log("delete", key, value)
          searchParams.set(key, "")
        }
      }
    )
    const url = url_.replace(/\%2C/g, ",")
    return url
  }

  const onChange = (paramName, paramValue) => {
    updateSearchParams(paramName, paramValue)
    const url = searchParamsToUrl(searchParams)
    navigate(
      url,
      {
        state: {
          refocusId: paramName,
          disableScrollUpdate: true,
        }
      }
    )
  }

  const paramToShipOptions = (shipStr) => {
    const ship = Number(shipStr)
    return shipOptions.find((option) => option.value === ship)
  }

  const paramToCardOptions = (cards) => {
    if (cards) {
      const foo = []

      cards.split(",").forEach(card => {
        const option = cardOptions.find((option) => option.value === card)
        if (option) {
          foo.push(option)
        }
      })
      return foo

    }
    return []
  }

  const parseParams = (searchParams) => {
    const params = {
      attacker_hand: paramToCardOptions(searchParams.get("attacker_hand") || ""),
      defender_hand: paramToCardOptions(searchParams.get("defender_hand") || ""),
      attacker_ship: paramToShipOptions(searchParams.get("attacker_ship") || 1),
      defender_ship: paramToShipOptions(searchParams.get("defender_ship") || 1),
    }
    return params
  }

  const [unavailableAttackerCards, setUnavailableAttackerCards] = React.useState(new Set())
  const [unavailableDefenderCards, setUnavailableDefenderCards] = React.useState(new Set())
  const [attackerOptionsAreDisabled, setAttackerOptionsAreDisabled] = React.useState(false)
  const [defenderOptionsAreDisabled, setDefenderOptionsAreDisabled] = React.useState(false)
  const cardOptions = [
    { value: "ferocious", label: "Ferocious", description: "-1 combat bonus", advantage: -1},
    { value: "relentless", label: "Relentless", description: "Optionally re-roll your combat die once"},
    { value: "cruel", label: "Cruel", description: "Optionally re-roll your opponent's combat die once" },
    { value: "scrappy", label: "Scrappy", description: "On your turn, optionally re-roll your combat die once" },
    { value: "strategic", label: "Strategic", description: "-2 combat bonus if adjacent to another of you ships", advantage: -2 },
    { value: "rational", label: "Rational", description: "Your combat die always rolls to 3"},
    { value: "stubborn", label: "Stubborn", description: "As defender, break ties (and destroy your attacker if they lose)" },
  ]

  const shipOptions = [
    {value: 1, label: "⚀ 1 (Battlestation)"},
    {value: 2, label: "⚁ 2 (Flagship)"},
    {value: 3, label: "⚂ 3 (Destroyer)"},
    {value: 4, label: "⚃ 4 (Frigate)"},
    {value: 5, label: "⚄ 5 (Interceptor)"},
    {value: 6, label: "⚅ 6 (Scout)"},
  ]

  // const validUrlParamKeys = new Set([...cardOptions, shipOptions].map(option => option.))
  // const validUrlParamValues = new Set([...cardOptions, shipOptions].map(option => option.value))

  const url_params = location.search
  const searchParams = new URLSearchParams(new URL(location.href).search)

  

  const newParams = parseParams(searchParams)
  const defaultFormState = newParams
  const [formState, setFormState] = React.useState(defaultFormState)

  // Set the form state ONLY when the URL changes! This avoids infinite loops
  React.useEffect(() => {
    setFormState(defaultFormState)
    const attacker_hand = defaultFormState.attacker_hand || []
    setUnavailableAttackerCards(attacker_hand.map(option => option.value))
    setAttackerOptionsAreDisabled(attacker_hand.length >= 3)
    const defender_hand = defaultFormState.defender_hand || []
    setUnavailableDefenderCards(defender_hand.map(option => option.value))
    setDefenderOptionsAreDisabled(defender_hand.length >= 3)
  }, [location])


  // Update "available cards", so that unavailable cards won't be shown in either
  // attacker or defender hand selection
  const allSelectedCards = new Set([...unavailableAttackerCards, ...unavailableDefenderCards])
  const availableCards = []
  cardOptions.forEach(option => {
    if (!allSelectedCards.has(option.value)) {
      availableCards.push(option.value)
    }
  })

  const [explanation, attackerWinRatio] = genExplanation(
    formState.attacker_ship,
    formState.attacker_hand.map((option) => option.value),
    formState.defender_ship,
    formState.defender_hand.map((option) => option.value),
    rawData
  )

  const swapSides = () => {
    const {attacker_ship, attacker_hand, defender_ship, defender_hand} = formState
    formState.attacker_ship = defender_ship
    formState.attacker_hand = defender_hand
    formState.defender_ship = attacker_ship
    formState.defender_hand = attacker_hand
    console.log("url old", searchParams.toString())
    updateSearchParams("attacker_ship", formState.attacker_ship)
    updateSearchParams("attacker_hand", formState.attacker_hand)
    updateSearchParams("defender_ship", formState.defender_ship)
    updateSearchParams("defender_hand", formState.defender_hand)
    const url = searchParamsToUrl(searchParams)
    
    console.log("url new", searchParams.toString())
    navigate(
      url,
      {
        state: {
          disableScrollUpdate: true,
        }
      }
    )

  }
  console.log("attacker_hand", formState.attacker_hand)
  return (
    <div>
      <Button onClick={() => navigate(location.pathname)}>Reset</Button>
      <Form>
        <Form.Row>
          <Col sm className="calc-side">
              <Form.Label htmlFor="attacker_ship">{"Attacker Ship"}</Form.Label>
              <Select
                id="attacker_ship"
                name="attacker_ship"
                options={shipOptions}
                value={formState.attacker_ship}
                onChange={(selection) => onChange("attacker_ship", selection)}
              />
              <Form.Label htmlFor="attacker_dropdown">{"Attacker Hand"}</Form.Label>
              <CardSelect
                id="attacker_dropdown"
                value={formState.attacker_hand}
                options={cardOptions}
                availableCards={availableCards}
                onChange={(selection) => onChange("attacker_hand", selection)}
                optionsAreDisabled={attackerOptionsAreDisabled}
                placeholder="Empty"
              />
              <HandExplanation hand={formState.attacker_hand} />
          </Col>

          <Col sm={1} className="text-center my-auto" >
            <p>vs.</p>
            <Button title="Swap sides" size="sm" variant="secondary" onClick={swapSides}>⇄</Button>
          </Col>

          <Col sm className="calc-side">
              <Form.Label htmlFor="defender_ship">{"Defender Ship"}</Form.Label>
              <Select
                id="defender_ship"
                name="defender_ship"
                options={shipOptions}
                value={formState.defender_ship}
                onChange={(selection) => onChange("defender_ship",  selection)}
              />
              <Form.Label htmlFor="defender_dropdown">{"Defender Hand"}</Form.Label>
              <CardSelect
                id="defender_dropdown"
                options={cardOptions}
                value={formState.defender_hand}
                availableCards={availableCards}
                onChange={(selection) => onChange("defender_hand", selection)}
                optionsAreDisabled={defenderOptionsAreDisabled}
                placeholder="Empty"
              />
              <HandExplanation hand={formState.defender_hand} />
          </Col>
          
          <Col sm={1} className="text-center my-auto" ><InlineMath>=</InlineMath></Col>

          <Col sm className="calc-side">
            <Results attackerWinRatio={attackerWinRatio} {...formState} />
          </Col>
        </Form.Row>
      </Form>
    </div>
  )
}
// <p>{explanation}: <b>{formatRatio(attackerWinRatio)}</b></p>

export default Calc


