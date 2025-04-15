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
  connectionAttributes: any;
}

export type DataSourceCreationModel = Omit<DataSource, 'id'>; 
