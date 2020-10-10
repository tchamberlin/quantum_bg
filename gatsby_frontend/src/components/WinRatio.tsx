import React from "react"

import { InlineMath, BlockMath } from "react-katex"

import { categorizeWinRatio, formatRatio } from "./utilities"

const WinRatio = ({ ratio, children }) => {
  const [showFullPrecision, setShowFullPrecision] = React.useState(false)
  const ratioDisplay = showFullPrecision ? `${ratio * 100}` : formatRatio(ratio)
  return (
    <p className={`results ${categorizeWinRatio(ratio)}`}>
      {children}
      <br />
      <div
        title="Click to toggle full-precision display"
        className={
          showFullPrecision
            ? "toggle-precision full-precision"
            : "toggle-precision"
        }
        onClick={() => setShowFullPrecision(!showFullPrecision)}
      >
        <BlockMath>{`${ratioDisplay}\\%`}</BlockMath>
      </div>
    </p>
  )
}

export default WinRatio
