// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

// import React, { useEffect, useState } from "react"
// import { Divider, Form, Input, Select } from "antd"
// import OutputHandle from "../OutputHandle"
// import InputHandle from "../InputHandle"
// import { LunarFormerCard } from "../baseCard/LunarFormerCard"
// import GenericCardTypeProps from "./GenericCardTypeProps"
// import { mapKVToObject } from "@/utils/mappers"
// import { useForm } from "antd/es/form/Form"

// const attributesOptions = [
//   { label: 'News', value: 'news' },
//   { label: 'Feedback', value: 'feedback' },
//   { label: 'Asset Profile', value: 'assetProfile' },
//   { label: 'Balance Sheet History', value: 'balanceSheetHistory' },
//   { label: 'Balance Sheet History Quarterly', value: 'balanceSheetHistoryQuarterly' },
//   { label: 'Calendar Events', value: 'calendarEvents' },
//   { label: 'Cashflow Statement History', value: 'cashflowStatementHistory' },
//   { label: 'Cashflow Statement History Quarterly', value: 'cashflowStatementHistoryQuarterly' },
//   { label: 'Default Key Statistics', value: 'defaultKeyStatistics' },
//   { label: 'Earnings', value: 'earnings' },
//   { label: 'Earnings History', value: 'earningsHistory' },
//   { label: 'Earnings Trend', value: 'earningsTrend' },
//   { label: 'Esg Scores', value: 'esgScores' },
//   { label: 'Financial Data', value: 'financialData' },
//   { label: 'Fund Ownership', value: 'fundOwnership' },
//   { label: 'Fund Performance', value: 'fundPerformance' },
//   { label: 'Fund Profile', value: 'fundProfile' },
//   { label: 'Index Trend', value: 'indexTrend' },
//   { label: 'Income Statement History', value: 'incomeStatementHistory' },
//   { label: 'Income Statement History Quarterly', value: 'incomeStatementHistoryQuarterly' },
//   { label: 'Industry Trend', value: 'industryTrend' },
//   { label: 'Insider Holders', value: 'insiderHolders' },
//   { label: 'Insider Transactions', value: 'insiderTransactions' },
//   { label: 'Institution Ownership', value: 'institutionOwnership' },
//   { label: 'Major Holders Breakdown', value: 'majorHoldersBreakdown' },
//   { label: 'Page Views', value: 'pageViews' },
//   { label: 'Price', value: 'price' },
//   { label: 'Quote Type', value: 'quoteType' },
//   { label: 'Recommendation Trend', value: 'recommendationTrend' },
//   { label: 'Sec Filings', value: 'secFilings' },
//   { label: 'Net Share Purchase Activity', value: 'netSharePurchaseActivity' },
//   { label: 'Sector Trend', value: 'sectorTrend' },
//   { label: 'Summary Detail', value: 'summaryDetail' },
//   { label: 'Summary Profile', value: 'summaryProfile' },
//   { label: 'Top Holdings', value: 'topHoldings' },
//   { label: 'Upgrade Downgrade History', value: 'upgradeDowngradeHistory' }
// ]

// export const YahooFinanceExtractorCard: React.FC<GenericCardTypeProps> = ({ data, id }) => {

//   const [parameters, setParameters] = useState<string[]>([])
//   const [changing, setChanging] = useState<boolean>(false)
//   const [form] = useForm()

//   useEffect(() => {

//     const keys = Object.keys(data.variables)
//     keys.forEach((key, i) => {
//       form.setFieldValue(key + i, data.variables[key].split(','))
//     })
//     console.log()
//     form.setFieldValue('symbols', data.inputs['symbols'])
//     form.setFieldValue('attributes', data.inputs['attributes'])
//     setChanging(prev => !prev)
//   }, [])

//   useEffect(() => {
//     data.setNodes((nds) =>
//       nds.map((node) => {
//         if (node.id === id) {
//           node.data = {
//             ...node.data,
//           };
//         }

//         return node;
//       })
//     );
//   }, [form.getFieldValue('input'), changing]);

//   return <LunarFormerCard
//     id={id}
//     component={data}
//   >
//     <Form layout="vertical" form={form} initialValues={{ input: 'Extract {attributes} from {symbols}', attributes: [] }}>
//       <InputHandle name="Context" />
//       <Divider style={{ margin: '16px 0', minWidth: 300 }} />
//       <Form.Item
//         label="Symbols"
//         labelAlign="left"
//         name="symbols"
//         required
//         wrapperCol={{ span: 24 }}
//       >
//         <Input
//           name="symbols"
//           onChange={event => {
//             form.setFieldValue('symbols', event.target.value)
//           }}
//         />
//       </Form.Item>
//       <Form.Item
//         label="Attributes"
//         labelAlign="left"
//         name="attributes"
//         required
//         wrapperCol={{ span: 24 }}
//       >
//         <Select
//           mode="multiple"
//           allowClear
//           className="nodrag nowheel"
//           style={{ width: '100%' }}
//           placeholder="Please select"
//           onChange={(value) => {
//             setChanging(prev => !prev)
//             form.setFieldValue('attributes', value)
//           }}
//           options={attributesOptions}
//         />
//       </Form.Item>
//       <Divider style={{ margin: '16px 0', minWidth: 300 }} />
//       <OutputHandle name="Output" />
//     </Form>
//   </LunarFormerCard>
// }
