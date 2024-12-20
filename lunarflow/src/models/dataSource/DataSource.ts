export interface DataSourceType {
  id: string;
  name: string;
  connectionAttributes: string[];
}

export interface DataSource {
  id: string;
  name: string;
  description: string;
  type: string;
  connectionAttributes: Record<string, string>;
}

export type DataSourceCreationModel = Omit<DataSource, 'id'>; 
