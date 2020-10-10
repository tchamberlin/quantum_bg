import round from "lodash/round"
import floor from "lodash/floor"

export function categorizeWinRatio(attacker_win_ratio) {
  let resultsCategory
  if (attacker_win_ratio > 0.7) {
    resultsCategory = "results-good"
  } else if (attacker_win_ratio > 0.5) {
    resultsCategory = "results-medium"
  } else {
    resultsCategory = "results-bad"
  }
  return resultsCategory
}

export function roundToN(x, n) {
  return round(x, -Number(floor(Math.log10(x))) + (n - 1))
}
export function formatRatio(ratio) {
  return `${round(ratio * 100, 2)}`
}
