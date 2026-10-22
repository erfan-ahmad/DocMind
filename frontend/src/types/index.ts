export interface User {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  full_name?: string;
  is_active?: boolean;
  date_joined?: string;
}

export interface Category {
  id: number;
  name: string;
  description?: string;
  created_at?: string;
  owner?: number;
}

export interface Document {
  id: number;
  title: string;
  description: string;
  category: number;
  file?: string;
  file_name: string;
  file_size: number;
  mime_type: string;
  status: "UPLOADED" | "PROCESSING" | "PROCESSED" | "INDEXED" | "FAILED";
  created_at: string;
  updated_at: string;
  extracted_text?: string;
  error_message?: string;
  owner?: number;
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

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}