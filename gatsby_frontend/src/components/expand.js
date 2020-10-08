import all_data from '../results'

export function expand() {
    const result = []
    Object.keys(all_data).forEach((attacker_advantage) => {
        Object.keys(all_data[attacker_advantage]).forEach((attacker_hand) => {
            Object.keys(all_data[attacker_advantage][attacker_hand]).forEach((defender_hand) => {
                result.push({
                    attacker_advantage: attacker_advantage,
                    attacker_hand: attacker_hand.split("|"),
                    defender_hand: defender_hand.split("|"),
                    win_ratio: all_data[attacker_advantage][attacker_hand][defender_hand]
                })
            })
        })
    })
    return result
}
