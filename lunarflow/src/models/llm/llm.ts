export interface DataSourceType {
  id: string;
  name: string;
  expectedConnectionAttributes: string[];
}

export interface LLM {
  id: string;
  name: string;
  description: string;
  type: string;
  connectionAttributes: Record<string, string>;
}
