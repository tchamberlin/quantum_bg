// TODO: If number is small enough, show possible "outs" for disadvantaged attacks
// TODO: perhaps hoist URl state mechanics up to pages/calc.tsx. Don't think we
//       want _any_ gatsby/navigate stuff here
// TODO: First pass will have cards-per-encounter; this is way too much detail for
//       vast majority of use-cases. Should be opt-in; default should hold that state at the calc level
// TODO: Allow click-drag grouping of encounters with AND/OR operator, for use in final prob calc
// TODO: Introduce player_a/player_b language, since attacker/defender swaps when sides are swapped
//       This will allow us to carry card state through all encounters properly, regardless of swap state
// TODO: Custom widgets. Select is fine, but requires too many clicks/actions to do anything
// TODO: At some point, a generic prob calc would be pretty cool; we'll have done all the hard parts
// TODO: Sensible collapse behavior, pretty much everywhere
// TODO: Field that allows direct CLI-like input of "encounter notation". This should mirror
//       what is in the URL params, and should be smart (e.g. tab completion)
import React from "react"

import Select from "react-select"
import Button from "react-bootstrap/Button"
import Form from "react-bootstrap/Form"
import Col from "react-bootstrap/Col"
import Row from "react-bootstrap/Row"
import ButtonGroup from "react-bootstrap/ButtonGroup"
import { navigate } from "gatsby"

import isEqual from "lodash/isEqual"
import range from "lodash/range"

import { cardOptions, shipOptions } from "./constants"
import CloseButton from "./CloseButton"
import DisableButton from "./DisableButton"
import Encounter from "./Encounter"
import OverallResults from "./OverallResults"
import all_data from "../results"

const queryResults = ({
  attacker_ship,
  defender_ship,
  attacker_hand,
  defender_hand,
}) => {
  const attackerAdvantageKey = JSON.stringify(attacker_ship - defender_ship)
  const attackerHandKey = attacker_hand.sort().join("|")
  const defenderHandKey = defender_hand.sort().join("|")
  const attackerWinRatio =
    all_data[attackerAdvantageKey][attackerHandKey][defenderHandKey]

  return attackerWinRatio
}

const navigateSaveScroll = (url, state = {}) =>
  navigate(url, {
    state: {
      disableScrollUpdate: true,
      ...state,
    },
  })

const _default_encounter = {
  attacker_ship: 1,
  defender_ship: 1,
  attacker_hand: [],
  defender_hand: [],
}
const DEFAULT_ENCOUNTER = {
  ..._default_encounter,
  attacker_win_ratio: queryResults(_default_encounter),
}

export const Calc = ({ location }) => {
  const parseSideStr = sideStr => {
    // Caputure the first and second groups; throw out the full match at the front
    const [__, shipStr, handStr] = sideStr.match(/(\d)(?:\[([\s\w,]+)\])?/)
    const hand = handStr ? handStr.split(",").map(card => card.trim()) : []
    return [Number(shipStr), hand]
  }

  const parseEncounterStr = encounterStr => {
    const [attackerStr, defenderStr] = encounterStr.split(":")
    const [attackerShip, attackerHand] = parseSideStr(attackerStr)
    const [defenderShip, defenderHand] = parseSideStr(defenderStr)
    return {
      attacker_ship: attackerShip,
      attacker_hand: attackerHand,
      defender_ship: defenderShip,
      defender_hand: defenderHand,
    }
  }

  const urlParamsToEncounters = urlParams => {
    const encountersStrs = urlParams.getAll("encounter")
    const encounters = encountersStrs.map(encounterStr => {
      const encounter = parseEncounterStr(encounterStr)
      return { ...encounter, attacker_win_ratio: queryResults(encounter) }
    })

    return encounters
  }

  const encounterToUrlParams = ({
    attacker_ship,
    attacker_hand,
    defender_ship,
    defender_hand,
  }) => {
    const attackerHandPart = attacker_hand.length
      ? `[${attacker_hand.sort().join(",")}]`
      : ""
    const defenderHandPart = defender_hand.length
      ? `[${defender_hand.sort().join(",")}]`
      : ""
    const paramValue = `${attacker_ship}${attackerHandPart}:${defender_ship}${defenderHandPart}`
    return paramValue
  }

  const encountersToUrlParams = encounters => {
    const urlParams = new URLSearchParams()
    encounters.forEach((encounter, index) =>
      urlParams.append("encounter", encounterToUrlParams(encounter))
    )
    // URLSearchParams encodes reserved characters, which is quite ugly. We don't care about
    // reserved characters (static website and all that), so we simply decode it again
    // before sending it back
    return decodeURIComponent(urlParams)
  }

  const handleEncounterFieldChange = (
    paramName,
    paramValue,
    encounterIndex
  ) => {
    const newEncounter = { ...encounters[encounterIndex] }
    newEncounter[paramName] = paramValue
    const newEncounters = [
      ...encounters.slice(0, encounterIndex),
      newEncounter,
      ...encounters.slice(encounterIndex + 1),
    ]
    const url = `${location.pathname}?${encountersToUrlParams(newEncounters)}`
    // Send along the id of the field to re-focus too, to avoid weird behavior
    navigateSaveScroll(url, {
      state: {
        refocusId: paramName,
      },
    })
  }

  const swapSides = (encounters, encounterIndex) => {
    const encounter = encounters[encounterIndex]
    const swappedEncounter = { ...encounter }
    swappedEncounter.attacker_ship = encounter.defender_ship
    swappedEncounter.attacker_hand = encounter.defender_hand
    swappedEncounter.defender_ship = encounter.attacker_ship
    swappedEncounter.defender_hand = encounter.attacker_hand

    // Replace the "old" encounter with the "new" one -- this avoids mutating
    // any arguments/state
    const newEncounters = [
      ...encounters.slice(0, encounterIndex),
      swappedEncounter,
      ...encounters.slice(encounterIndex + 1),
    ]

    const url = `${location.pathname}?${encountersToUrlParams(newEncounters)}`
    navigateSaveScroll(url)
  }

  const addEncounter = encounters => {
    // If we've been given non-empty Encounters array, clone the last item
    // and append it to the array. Otherwise use the default Encounter object
    const encounter = encounters.length
      ? { ...encounters[encounters.length - 1] }
      : DEFAULT_ENCOUNTER
    const params = encountersToUrlParams([...encounters, encounter])
    const url = `${location.pathname}?${params}`
    navigateSaveScroll(url)
  }

  const removeEncounter = (encounters, index) => {
    const newEncounters = [
      ...encounters.slice(0, index),
      ...encounters.slice(index + 1),
    ]
    const params = encountersToUrlParams(newEncounters)
    const url = `${location.pathname}?${params}`
    navigateSaveScroll(url)
  }

  // START

  const url_params = location.search
  const searchParams = new URLSearchParams(new URL(location.href).search)

  const initialEncountersState = urlParamsToEncounters(searchParams)
  const defaultEncountersState = [DEFAULT_ENCOUNTER]

  if (!(initialEncountersState && initialEncountersState.length)) {
    const params = encountersToUrlParams(defaultEncountersState)
    const url = `${location.pathname}?${params}`
    navigateSaveScroll(url)
  }
  const [encounters, setEncounters] = React.useState(initialEncountersState)

  const [
    attackerOptionsAreDisabled,
    setAttackerOptionsAreDisabled,
  ] = React.useState(false)
  const [
    defenderOptionsAreDisabled,
    setDefenderOptionsAreDisabled,
  ] = React.useState(false)

  // Change encounters state ONLY when the URL changes! This avoids infinite loops
  React.useEffect(() => {
    setEncounters(urlParamsToEncounters(searchParams))
  }, [location])

  return (
    <div>
      <Row>
        <Col sm="auto">
          <Button onClick={() => navigate(location.pathname)}>Reset</Button>
        </Col>
        <Col>
          <Button onClick={() => addEncounter(encounters)}>
            Add Encounter
          </Button>
        </Col>
      </Row>
      <Form>
        {encounters.map((encounter, index) => (
          <Row className="results encounter-group">
            <Encounter
              encounter={encounter}
              onChange={(paramName, paramValue) =>
                handleEncounterFieldChange(paramName, paramValue, index)
              }
              attackerOptionsAreDisabled={attackerOptionsAreDisabled}
              defenderOptionsAreDisabled={defenderOptionsAreDisabled}
              swapSides={() => swapSides(encounters, index)}
            />
            <div className="close-button">
              <ButtonGroup vertical>
                <CloseButton
                  onClick={() => removeEncounter(encounters, index)}
                />
              </ButtonGroup>
            </div>
          </Row>
        ))}
      </Form>
      <hr />
      <OverallResults encounters={encounters} />
    </div>
  )
}

export default Calc
