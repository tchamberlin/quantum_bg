import React from "react"

import { InlineMath, BlockMath } from "react-katex"

import Button from "react-bootstrap/Button"
import sum from "lodash/sum"

import WinRatio from "./WinRatio"
import { categorizeWinRatio, formatRatio } from "./utilities"

const combine_probabilities_or = probabilities => {
  return 1 - probabilities.reduce((acc, current) => acc * (1 - current), 1)
}

const combine_probabilities_and = probabilities => {
  return probabilities.reduce((acc, current) => acc * current, 1)
}

const OverallResults = ({ encounters }) => {
  console.log("OverallResults", encounters)
  const ratios = encounters.map(encounter => encounter.attacker_win_ratio)
  const overall_probability_or = combine_probabilities_or(ratios)
  const overall_probability_and = combine_probabilities_and(ratios)
  return (
    <>
      <WinRatio ratio={overall_probability_and}>
        Probability of <em>all</em> attacks succeeding
      </WinRatio>
      <WinRatio ratio={overall_probability_or}>
        Probability of <em>at least one</em> attack succeeding:
      </WinRatio>
    </>
  )
}

export default OverallResults
