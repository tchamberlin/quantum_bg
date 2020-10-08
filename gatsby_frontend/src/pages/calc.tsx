import React from "react"
import { PageProps, Link, graphql } from "gatsby"

import Layout from "../components/layout"
import Calc from "../components/Calc"
import SEO from "../components/seo"
import all_data from '../results'

type DataProps = {
  site: {
    buildTime: string
  }
}

const UsingTypescript: React.FC<PageProps<DataProps>> = ({ data, path, ...props }) => (
  <Layout>
    <SEO title="Quantum Combat Calculator" />
    <Calc rawData={all_data} {...props} />
  </Layout>
)

export default UsingTypescript

export const query = graphql`
  {
    site {
      buildTime(formatString: "YYYY-MM-DD hh:mm a z")
    }
  }
`
