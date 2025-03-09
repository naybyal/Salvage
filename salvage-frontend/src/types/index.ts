export interface File {
  id: number;
  name: string;
  c_code: string;
  rust_code: string;
  created_at: string;
}

export interface AuthCredentials {
  username: string;
  password: string;
}

export interface TranspileResponse {
  rust_code: string;
}

export interface JWTTokens {
  access: string;
  refresh: string;
}