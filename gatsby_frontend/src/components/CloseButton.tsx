import React from "react"

import Button from "react-bootstrap/Button"

const CloseButton = ({ onClick, ...rest }) => (
  <Button onClick={onClick} variant="danger" size="sm" {...rest}>
    ✖
  </Button>
)

export default CloseButton
