import { Modal } from "antd"
import NewComponentForm from "../newComponentForm/NewComponentForm"

interface Props {
  id?: string
  open: boolean
  onCancel: () => void
  onClose: () => void
  onFinish?: (values: any) => void
}

const NewComponentModal: React.FC<Props> = ({ id, open, onCancel, onClose, onFinish }) => {
  return <Modal
    title="Component settings"
    open={open}
    onCancel={onCancel}
    onClose={onClose}
    footer={null}
  >
    <NewComponentForm id={id} onFinish={onFinish} />
  </Modal>
}

export default NewComponentModal
