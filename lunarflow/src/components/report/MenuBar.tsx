// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { Editor } from '@tiptap/react'
import { Button, ColorPicker, Menu, MenuProps, Popover, Space, message } from 'antd'
import {
  BoldOutlined,
  CodeOutlined,
  ItalicOutlined,
  OrderedListOutlined,
  RedoOutlined,
  StrikethroughOutlined,
  UndoOutlined,
  UnorderedListOutlined
} from '@ant-design/icons'
import { MenuClickEventHandler } from 'rc-menu/lib/interface'
import { useState } from 'react'
import { Report } from '@/models/Report'

interface MenuBarProps {
  editor: Editor | null
  report: Report
  convertHtmlToPdf: (htmlString: string) => Promise<Buffer>
  saveReport: (htmlString: string, reportName: string) => Promise<void>
}

type MenuItem = Required<MenuProps>['items'][number];

function getItem(
  label: React.ReactNode,
  key: React.Key,
  icon?: React.ReactNode,
  children?: MenuItem[],
  type?: 'group',
): MenuItem {
  return {
    key,
    icon,
    children,
    label,
    type,
  } as MenuItem;
}

const items: MenuProps['items'] = [
  getItem('Header 1', 'h1'),
  getItem('Header 2', 'h2'),
  getItem('Header 3', 'h3'),
  getItem('Header 4', 'h4'),
]

const MenuBar: React.FC<MenuBarProps> = ({ editor, report, convertHtmlToPdf, saveReport }) => {

  const [PDFLoading, setPDFLoading] = useState(false)
  const [saveLoading, setSaveLoading] = useState(false)
  const [messageApi, contextHolder] = message.useMessage()

  if (!editor) {
    return null
  }

  const onClick: MenuClickEventHandler = (menuInfo) => {
    switch (menuInfo.key) {
      case 'h1':
        editor.chain().focus().toggleHeading({ level: 1 }).run()
        break;

      case 'h2':
        editor.chain().focus().toggleHeading({ level: 2 }).run()
        break;

      case 'h3':
        editor.chain().focus().toggleHeading({ level: 3 }).run()
        break;

      case 'h4':
        editor.chain().focus().toggleHeading({ level: 4 }).run()
        break;

      default:
        break;
    }
    menuInfo.key
  }

  return (
    <Space style={{ position: 'fixed', backgroundColor: '#fff', zIndex: 10, paddingTop: 16, paddingBottom: 4, width: '100%' }}>
      {contextHolder}
      <Space.Compact>
        <Popover
          content={<Menu

            onClick={onClick}
            style={{ width: 256, border: 'none' }}
            defaultSelectedKeys={['1']}
            defaultOpenKeys={['sub1']}
            mode="inline"
            items={items}
          />}
        >
          <Button style={{ width: 105 }} size='large'>Heading {editor.getAttributes('heading').level}</Button>
        </Popover>

        <Button
          size='large'
          onClick={() => editor.chain().focus().toggleBold().run()}
          disabled={
            !editor.can()
              .chain()
              .focus()
              .toggleBold()
              .run()
          }
          className={editor.isActive('bold') ? 'is-active' : ''}
          icon={<BoldOutlined />}
        />
        <Button
          size='large'
          onClick={() => editor.chain().focus().toggleItalic().run()}
          disabled={
            !editor.can()
              .chain()
              .focus()
              .toggleItalic()
              .run()
          }
          className={editor.isActive('italic') ? 'is-active' : ''}
          icon={<ItalicOutlined />}
        />
        <Button
          size='large'
          onClick={() => editor.chain().focus().toggleStrike().run()}
          disabled={
            !editor.can()
              .chain()
              .focus()
              .toggleStrike()
              .run()
          }
          className={editor.isActive('strike') ? 'is-active' : ''}
          icon={<StrikethroughOutlined />}
        />
        <Button
          size='large'
          onClick={() => editor.chain().focus().toggleCode().run()}
          disabled={
            !editor.can()
              .chain()
              .focus()
              .toggleCode()
              .run()
          }
          className={editor.isActive('code') ? 'is-active' : ''}
          icon={<CodeOutlined />}
        />
        <Button
          size='large'
          onClick={() => editor.chain().focus().toggleBulletList().run()}
          className={editor.isActive('bulletList') ? 'is-active' : ''}
          icon={<UnorderedListOutlined />}
        />
        <Button
          size='large'
          onClick={() => editor.chain().focus().toggleOrderedList().run()}
          className={editor.isActive('orderedList') ? 'is-active' : ''}
          icon={<OrderedListOutlined />}
        />
        <Button
          size='large'
          onClick={() => editor.chain().focus().undo().run()}
          disabled={
            !editor.can()
              .chain()
              .focus()
              .undo()
              .run()
          }
          icon={<UndoOutlined />}
        />
        <Button
          size='large'
          onClick={() => editor.chain().focus().redo().run()}
          disabled={
            !editor.can()
              .chain()
              .focus()
              .redo()
              .run()
          }
          icon={<RedoOutlined />}
        />
        <Button
          size='large'
          onClick={async () => {
            setPDFLoading(true)
            try {
              const styledHTML = `${editor.getHTML()}<style>* {
                font-family: sans-serif;
               }</style>`
              const pdfBuffer = ((await convertHtmlToPdf(styledHTML)) as any).data
              const result = []
              for (var i in pdfBuffer) {
                result.push(pdfBuffer[i])
              }
              const buffer = new Uint8Array(result)
              const blob = new Blob([buffer], { type: 'application/pdf' })
              const anchor = document.createElement('a')
              anchor.href = window.URL.createObjectURL(blob)
              anchor.download = `Report.pdf`
              anchor.click()
            } catch (error) {
              messageApi.open({
                type: 'error',
                content: 'Failed to export the report'
              })
            } finally {
              setPDFLoading(false)
            }

          }}
          loading={PDFLoading}
        >
          Export to PDF
        </Button>
        <Button
          size='large'
          onClick={async () => {
            setSaveLoading(true)
            try {
              await saveReport(editor.getHTML(), report.name)
              messageApi.open({
                type: 'success',
                content: 'Your report has been saved'
              })
            } catch (error) {
              console.error(error)
              messageApi.open({
                type: 'error',
                content: 'Failed to save the report'
              })
            } finally {
              setSaveLoading(false)
            }
          }}
          loading={saveLoading}
        >
          Save
        </Button>
      </Space.Compact>
      <ColorPicker value={editor?.getAttributes('textStyle').color ?? '#000'} onChange={(color) => editor.chain().focus().setColor(color.toHexString()).run()} />
    </Space>
  )
}

export default MenuBar
