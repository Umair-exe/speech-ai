export interface ApiError {
  detail: string;
  status: number;
}

export interface CompressionResult {
  success: boolean;
  original_size: number;
  compressed_size: number;
  compression_ratio: number;
  original_dimensions: {
    width: number;
    height: number;
  };
  compressed_dimensions?: {
    width: number;
    height: number;
  };
  output_format: string;
  output_file: string;
  output_path: string;
  quality: number | string;
  duration?: string;
}
