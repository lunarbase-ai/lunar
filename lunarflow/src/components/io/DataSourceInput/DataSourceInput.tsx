import { getDataSourcesAction } from "@/app/actions/dataSources"
import FetchSelect from "@/components/select/fetchSelect"
import { useUserId } from "@/hooks/useUserId";
import { UploadOutlined } from "@ant-design/icons";
import { Button } from "antd";

interface DataSourceInputProps {
  value: string
  onInputChange: (value: { label: string; value: string }) => void
}

const DataSourceInput: React.FC<DataSourceInputProps> = ({ value, onInputChange }) => {

  const userId = useUserId()

  if (!userId) return <></>

  return <>
    <FetchSelect
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
    <Button
      style={{ width: '100%', marginTop: '16px' }}
      icon={<UploadOutlined />}
      href={`${process.env.NEXT_PUBLIC_HOST}/home/data-sources`}
      target="_blank"
    >
      Create a new data source
    </Button>
  </>
}

export default DataSourceInput
