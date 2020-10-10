export const cardOptions = [
  {
    value: "ferocious",
    label: "Ferocious",
    description: "-1 combat bonus",
    advantage: -1,
  },
  {
    value: "relentless",
    label: "Relentless",
    description: "Optionally re-roll your combat die once",
  },
  {
    value: "cruel",
    label: "Cruel",
    description: "Optionally re-roll your opponent's combat die once",
  },
  {
    value: "scrappy",
    label: "Scrappy",
    description: "On your turn, optionally re-roll your combat die once",
  },
  {
    value: "strategic",
    label: "Strategic",
    description: "-2 combat bonus if adjacent to another of you ships",
    advantage: -2,
  },
  {
    value: "rational",
    label: "Rational",
    description: "Your combat die always rolls to 3",
  },
  {
    value: "stubborn",
    label: "Stubborn",
    description:
      "As defender, break ties (and destroy your attacker if they lose)",
  },
]

export const shipOptions = [
  { value: 1, label: "⚀ 1 (Battlestation)" },
  { value: 2, label: "⚁ 2 (Flagship)" },
  { value: 3, label: "⚂ 3 (Destroyer)" },
  { value: 4, label: "⚃ 4 (Frigate)" },
  { value: 5, label: "⚄ 5 (Interceptor)" },
  { value: 6, label: "⚅ 6 (Scout)" },
]
