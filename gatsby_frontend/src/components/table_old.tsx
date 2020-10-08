const applyFilters = (data, setData, selectedAttackerAdvantage, unavailableAttackerCards, unavailableDefenderCards) => {
  const _data = data.filter(
    ({ attacker_advantage, attacker_hand, defender_hand }) => {
      if (attacker_hand[0] === "") {
        attacker_hand = []
      }
      if (defender_hand[0] === "") {
        defender_hand = []
      }
      return (
        attacker_advantage == selectedAttackerAdvantage &&
        (isEqual(new Set(attacker_hand), new Set(unavailableAttackerCards))) &&
        (isEqual(new Set(defender_hand), new Set(unavailableDefenderCards)))
      )
    }
  )
  // setData(_data)
}
