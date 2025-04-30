import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { atomOneLight } from 'react-syntax-highlighter/dist/esm/styles/hljs'

interface MarkdownRendererProps {
  content: string;
}

const MarkdownOutput: React.FC<MarkdownRendererProps> = ({ content }) => {
  return (
    <ReactMarkdown
      components={{
        code(props) {
          const { children, className, node, ...rest } = props
          const match = /language-(\w+)/.exec(className || '')
          return match ? (
            <SyntaxHighlighter
              language={match[1]}
              style={atomOneLight}
            >
              {String(children).replace(/\n$/, '')}
            </SyntaxHighlighter>
          ) : (
            <code {...rest} className={className}>
              {children}
            </code>
          )
        }
      }}
      remarkPlugins={[remarkGfm, remarkMath]}
    >
      {content}
    </ReactMarkdown>
  );
};

export default MarkdownOutput;
