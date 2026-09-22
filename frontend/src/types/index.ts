export interface User {
  id: number;
  username: string;
  email: string;
}

export interface Category {
  id: number;
  name: string;
  description?: string;
}

export interface Document {
  id: number;
  title: string;
  description: string;
  file_name: string;
  file_size: number;
  mime_type: string;
  status: "UPLOADED" | "PROCESSING" | "PROCESSED" | "INDEXED" | "FAILED";
  created_at: string;
  updated_at: string;
  extracted_text?: string;
  error_message?: string;
}

export interface Source {
  document_id: number;
  document_title: string;
  chunk_index: number;
  score: number;
  text: string;
}

export interface AskResponse {
  query: string;
  answer: string;
  sources: Source[];
}