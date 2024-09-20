// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

'use client'
import { Color } from '@tiptap/extension-color'
import ListItem from '@tiptap/extension-list-item'
import TextStyle from '@tiptap/extension-text-style'
import Image from '@tiptap/extension-image'
import Table from '@tiptap/extension-table'
import TableCell from '@tiptap/extension-table-cell'
import TableHeader from '@tiptap/extension-table-header'
import TableRow from '@tiptap/extension-table-row'
import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import './tiptap.css'
import { Report } from '@/models/Report'
import MenuBar from './MenuBar'

interface TipTapProps {
  report: Report
  convertHtmlToPdf: (htmlString: string) => Promise<Buffer>
  saveReport: (htmlString: string, reportName: string) => Promise<void>
}

const Tiptap: React.FC<TipTapProps> = ({ report, convertHtmlToPdf, saveReport }) => {
  const editor = useEditor({
    extensions: [
      Color.configure({ types: [TextStyle.name, ListItem.name] }),
      TextStyle,
      Image.configure({
        allowBase64: true,
      }),
      Table.configure({
        resizable: true,
      }),
      TableRow,
      TableHeader,
      TableCell,
      StarterKit.configure({
        bulletList: {
          keepMarks: true,
          keepAttributes: false,
        },
        orderedList: {
          keepMarks: true,
          keepAttributes: false,
        },
      }),
    ],
    content: report.content,

  })

  return (
    <>
      <MenuBar editor={editor} report={report} convertHtmlToPdf={convertHtmlToPdf} saveReport={saveReport} />
      <EditorContent editor={editor} />
    </>
  )
}

export default Tiptap