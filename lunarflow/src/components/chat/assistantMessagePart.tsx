import { Button, Divider, Table } from "antd";
import MarkdownOutput from "../io/MarkdownOutput/MarkdownOutput";
import { LunarAgentEvent } from "@/app/api/chat/types";
import { Message } from "ai";
import ChatAgentRunConfirmation from "./chatAgentRunConfirmation";
import AgentDataItem from "./agentDataItem";
import { Bar, Line } from "react-chartjs-2";

type MessagePart = NonNullable<Message['parts']>[number];

interface AssistantMessagePartProps {
  messagePart: MessagePart
  userId: string
  index: number
  addToolResult: ({ toolCallId, result, }: {
    toolCallId: string;
    result: any;
  }) => void
  agentData?: LunarAgentEvent[]
}

const AssistantMessagePart: React.FC<AssistantMessagePartProps> = ({
  messagePart,
  userId,
  addToolResult,
  agentData,
  index
}) => {
  switch (messagePart.type) {
    case 'step-start':
      return index !== 0 ? <Divider></Divider> : <div style={{ marginTop: 16 }}></div>
    case 'text':
      return <MarkdownOutput content={messagePart.text} />
    case 'tool-invocation':
      const { toolCallId, state, args } = messagePart.toolInvocation;

      if (messagePart.toolInvocation.toolName === 'barChart') {
        return <div key={toolCallId} className='h-[500px] m-4'>
          <Bar
            width='100%'
            data={{
              ...args,
              datasets: args.datasets?.map((dataset: any) => ({
                ...dataset,
                backgroundColor: '#1E3257'
              }))
            }}
            options={{
              responsive: true,
              maintainAspectRatio: false
            }} />
        </div>
      } else if (messagePart.toolInvocation.toolName === 'lineChart') {
        return <div key={toolCallId} className='h-[300px] m-4'>
          <Line
            data={{
              ...args,
              datasets: args.datasets?.map((dataset: any) => ({
                ...dataset,
                borderColor: '#1E3257'
              }))
            }}
            options={{
              responsive: true,
              maintainAspectRatio: false
            }} />
        </div>
      } else if (messagePart.toolInvocation.toolName === 'displayTable') {
        const { headers, rows } = args!;
        const columns = headers.map((header: string) => ({ title: header, dataIndex: header, key: header }));
        const dataSource = rows.map((row: string[], index: number) => {
          const rowData: Record<string, any> = { key: index };
          headers.forEach((header: string, idx: number) => {
            rowData[header] = row[idx];
          });
          return rowData;
        });

        const downloadCSV = () => {
          const csvContent = [
            headers.join(';'),
            ...rows.map((row: string[]) => row.join(';'))
          ].join('\n');

          const utf8BOM = '\uFEFF';
          const blob = new Blob([utf8BOM + csvContent], { type: 'text/csv;charset=utf-8;' });

          const url = URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          link.setAttribute('download', 'table_data.csv');
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
        };

        return (
          <>
            <div className="w-full px-6 mt-8">
              <div className="max-w-[1200px] mx-auto mb-2 flex justify-between items-center">
                <div className="flex gap-6">
                  <Button
                    type="default"
                    style={{ background: 'transparent' }}
                    onClick={downloadCSV}
                    loading={false}
                    disabled={rows.length === 0}
                  >
                    Exportar tabela como CSV
                  </Button>
                </div>
              </div>
              <div className="max-w-[1200px] w-full bg-background-default p-6 rounded-lg mx-auto">
                <Table
                  size="small"
                  dataSource={dataSource}
                  columns={columns}
                  scroll={{ x: true }}
                  pagination={{ pageSize: 20 }}
                />
              </div>
            </div>
          </>
        );
      }

      if (state === 'call') return <ChatAgentRunConfirmation
        toolInvocation={messagePart.toolInvocation}
        addToolResult={addToolResult}
      />
      const agentDataItems = agentData?.filter(agent => agent.toolCallId === toolCallId)
      return <div style={{ width: '100%', display: 'flex', flexDirection: 'column' }} key={toolCallId}>
        {agentDataItems?.map((agentDataItem, index) => {
          const agentInvocationItemsLength = agentDataItems.length
          return <AgentDataItem
            event={agentDataItem}
            index={index}
            numberOfEvents={agentInvocationItemsLength}
            toolCallId={toolCallId}
          />
        })}
      </div>
    default:
      console.error('Unknown part type:', messagePart.type, messagePart)
  }
}

export default AssistantMessagePart
