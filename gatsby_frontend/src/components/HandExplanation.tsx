import React from "react"

const HandExplanation = ({ hand }) => {
  if (hand.length) {
    console.log("HandExplanation hand", hand)
    return (
      <>
        <hr />
        <ul>
          {hand.map(option => (
            <li>
              <b>{option.label}</b>: {option.description}
            </li>
          ))}
        </ul>
      </>
    )
  }
  return null
}

export default HandExplanation
