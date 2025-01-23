import { getDataSourcesAction } from "@/app/actions/dataSources"
import FetchSelect from "@/components/select/fetchSelect"
import { useUserId } from "@/hooks/useUserId";

interface DataSourceInputProps {
  value: string
  onInputChange: (value: { label: string; value: string }) => void
}

const DataSourceInput: React.FC<DataSourceInputProps> = ({ value, onInputChange }) => {

  const userId = useUserId()

  if (!userId) return <></>

  return <FetchSelect
    onChange={(value) => {
      if (Array.isArray(value)) return
      onInputChange(value)
    }}
    fetchOptions={async () => {
      const dataSources = await getDataSourcesAction(userId)
      return dataSources.map(dataSource => {
        return { label: dataSource.name, value: dataSource.id }
      })
    }} />
}

export default DataSourceInput
