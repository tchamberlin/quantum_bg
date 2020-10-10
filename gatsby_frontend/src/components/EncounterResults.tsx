import React from "react"

import { InlineMath, BlockMath } from "react-katex"

import sum from "lodash/sum"

import WinRatio from "./WinRatio"
import { categorizeWinRatio, formatRatio } from "./utilities"

const calcAdvantage = (selected_ship_option, selected_card_options) => {
  const cardsWithAdvantage = selected_card_options.filter(
    option => typeof option.advantage !== "undefined"
  )
  return sum(cardsWithAdvantage.map(option => option.advantage))
}

const EncounterResults = ({
  attacker_ship,
  defender_ship,
  attacker_hand,
  defender_hand,
  attacker_win_ratio,
}) => {
  const rawAdvantage = attacker_ship - defender_ship
  const effectiveAdvantage =
    calcAdvantage(attacker_ship, attacker_hand) -
    calcAdvantage(defender_ship, defender_hand)
  const rawAdvantageHelp =
    '"Raw advantage" is simply the attacker ship die minus the defender ship ' +
    "die. So, lower numbers are better for the attacker"
  const effectiveAdvantageHelp =
    '"Effective advantage" is (attacker_ship_die + advantage_from_cards) - ' +
    "(defender_ship_die + advantage_from_cards). So, lower numbers are better for the attacker"

  const resultsCategory = categorizeWinRatio(attacker_win_ratio)

  const effectiveAttackerEq = `(${attacker_ship} + ${calcAdvantage(
    attacker_ship,
    attacker_hand
  )})`
  const effectiveDefenderEq = `(${defender_ship} + ${calcAdvantage(
    defender_ship,
    defender_hand
  )})`
  const effectiveCombatEq = `${effectiveAttackerEq} - ${effectiveDefenderEq} = ${effectiveAdvantage}`
  return (
    <>
      <p title={rawAdvantageHelp}>
        Raw combat advantage:
        <br />
        <BlockMath>{`${attacker_ship} - ${defender_ship} = ${rawAdvantage}`}</BlockMath>
      </p>
      <p title={effectiveAdvantageHelp}>
        Effective combat advantage:
        <br />
        <BlockMath>{effectiveCombatEq}</BlockMath>
      </p>
      <hr />
      <WinRatio ratio={attacker_win_ratio}>Attacker Win Ratio:</WinRatio>
    </>
  )
}

export default EncounterResults
