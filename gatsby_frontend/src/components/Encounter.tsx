import React from "react"

import Select from "react-select"
import Button from "react-bootstrap/Button"
import Col from "react-bootstrap/Col"
import Form from "react-bootstrap/Form"
import { InlineMath, BlockMath } from "react-katex"

import EncounterResults from "./EncounterResults"
import CardSelect from "./CardSelect"
import HandExplanation from "./HandExplanation"
import { cardOptions, shipOptions } from "./constants"

const buildOptions = (start, end) =>
  range(start, end + 1).map(item => ({ value: item, label: item }))

const Encounter = ({
  encounter: {
    attacker_ship,
    attacker_hand,
    defender_ship,
    defender_hand,
    attacker_win_ratio,
  },
  onChange,
  attackerOptionsAreDisabled,
  defenderOptionsAreDisabled,
  swapSides,
}) => {
  // Update "available cards", so that unavailable cards won't be shown in either
  // attacker or defender hand selection
  const allSelectedCards = new Set([...attacker_hand, ...defender_hand])
  const availableCards = []
  cardOptions.forEach(option => {
    if (!allSelectedCards.has(option.value)) {
      availableCards.push(option.value)
    }
  })

  return (
    <>
      <Col sm className="calc-side mx-auto">
        <Form.Label htmlFor="attacker_ship">{"Attacker Ship"}</Form.Label>
        <Select
          id="attacker_ship"
          name="attacker_ship"
          options={shipOptions}
          value={shipOptions.find(option => option.value === attacker_ship)}
          onChange={selection => onChange("attacker_ship", selection.value)}
        />
        <Form.Label htmlFor="attacker_dropdown">{"Attacker Hand"}</Form.Label>
        <CardSelect
          id="attacker_dropdown"
          value={cardOptions.filter(option =>
            attacker_hand.some(card => option.value === card)
          )}
          options={cardOptions}
          availableCards={availableCards}
          onChange={selection =>
            onChange(
              "attacker_hand",
              selection.map(option => option.value)
            )
          }
          optionsAreDisabled={attacker_hand.length >= 3}
          placeholder="Empty"
        />
        <HandExplanation
          hand={attacker_hand.map(card =>
            cardOptions.find(option => option.value === card)
          )}
        />
      </Col>

      <Col sm={1} className="text-center my-auto">
        <p>vs.</p>
        <Button
          title="Swap sides"
          size="sm"
          variant="secondary"
          onClick={swapSides}
        >
          ⇄
        </Button>
      </Col>

      <Col sm className="calc-side">
        <Form.Label htmlFor="defender_ship">{"Defender Ship"}</Form.Label>
        <Select
          id="defender_ship"
          name="defender_ship"
          options={shipOptions}
          value={shipOptions.find(option => option.value === defender_ship)}
          onChange={selection => onChange("defender_ship", selection.value)}
        />
        <Form.Label htmlFor="defender_dropdown">{"Defender Hand"}</Form.Label>
        <CardSelect
          id="defender_dropdown"
          options={cardOptions}
          value={cardOptions.filter(option =>
            defender_hand.some(card => option.value === card)
          )}
          availableCards={availableCards}
          onChange={selection =>
            onChange(
              "defender_hand",
              selection.map(option => option.value)
            )
          }
          optionsAreDisabled={defender_hand.length >= 3}
          placeholder="Empty"
        />
        <HandExplanation
          hand={defender_hand.map(card =>
            cardOptions.find(option => option.value === card)
          )}
        />
      </Col>

      <Col sm={1} className="text-center my-auto">
        <InlineMath>=</InlineMath>
      </Col>

      <Col sm className="calc-side">
        <EncounterResults
          attacker_ship={attacker_ship}
          defender_ship={defender_ship}
          attacker_hand={attacker_hand}
          defender_hand={defender_hand}
          attacker_win_ratio={attacker_win_ratio}
        />
      </Col>
    </>
  )
}

export default Encounter
