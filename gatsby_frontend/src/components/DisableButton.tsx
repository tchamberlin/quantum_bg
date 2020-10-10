import React from "react"

import Button from "react-bootstrap/Button"

const DisableButton = ({ onClick, ...rest }) => (
  <Button onClick={onClick} variant="warning" size="sm" {...rest}>
    ⏼
  </Button>
)

export default DisableButton
