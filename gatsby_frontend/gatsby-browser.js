/**
 * Implement Gatsby's Browser APIs in this file.
 *
 * See: https://www.gatsbyjs.com/docs/browser-apis/
 */

// You can delete this file if you're not using it
import "./src/styles/global.css"

// Used to avoid resetting scroll position in the Quantum Combat Calculator
export const shouldUpdateScroll = ({ routerProps }) => {
  if (typeof routerProps.location.state === 'undefined') {
    return true
  }

  const { disableScrollUpdate } = routerProps.location.state
  return !disableScrollUpdate
}

// Used to avoid resetting element focusing Quantum Combat Calculator
export const onRouteUpdate = loc => {
  const { state } = loc.location
  if (state && state.refocusId) {
    const elem = document.getElementById(state.refocusId)
    if (elem) {
      elem.focus()
    }
  }
}
