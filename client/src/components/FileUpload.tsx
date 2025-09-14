import React, { useState, useRef } from 'react';
import { Upload, File, X, CheckCircle, AlertCircle } from 'lucide-react';

interface FileUploadProps {
  onUploadSuccess: () => void;
}

interface UploadResult {
  success: boolean;
  message: string;
  filename?: string;
}

const FileUpload: React.FC<FileUploadProps> = ({ onUploadSuccess }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<UploadResult | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const supportedFormats = ['.pdf', '.doc', '.docx', '.txt'];
  const maxFileSize = 10 * 1024 * 1024; // 10MB

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const validateFile = (file: File): string | null => {
    const fileExt = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
    
    if (!supportedFormats.includes(fileExt)) {
      return `Unsupported file format. Supported formats: ${supportedFormats.join(', ')}`;
    }

    if (file.size > maxFileSize) {
      return `File size too large. Maximum size: ${maxFileSize / (1024 * 1024)}MB`;
    }

    return null;
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      const file = files[0];
      const validationError = validateFile(file);
      if (validationError) {
        setUploadResult({ success: false, message: validationError });
        return;
      }
      setSelectedFile(file);
      setUploadResult(null);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      const file = files[0];
      const validationError = validateFile(file);
      if (validationError) {
        setUploadResult({ success: false, message: validationError });
        return;
      }
      setSelectedFile(file);
      setUploadResult(null);
    }
  };

  const uploadFile = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    setUploadResult(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('customer_email', 'upload@example.com');

      const response = await fetch(`${API_BASE_URL}/api/upload`, {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (result.success) {
        setUploadResult({
          success: true,
          message: `File "${selectedFile.name}" uploaded and classified successfully!`,
          filename: selectedFile.name
        });
        setSelectedFile(null);
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
        onUploadSuccess();
      } else {
        setUploadResult({
          success: false,
          message: result.error || 'Upload failed'
        });
      }
    } catch (error) {
      setUploadResult({
        success: false,
        message: `Upload error: ${error instanceof Error ? error.message : 'Unknown error'}`
      });
    } finally {
      setIsUploading(false);
    }
  };

  const clearSelection = () => {
    setSelectedFile(null);
    setUploadResult(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const openFileDialog = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="file-upload-section">
      <div className="file-upload-header">
        <h2>📁 Upload Support Documents</h2>
        <p>Upload PDF, DOC, DOCX, or TXT files to automatically classify them as support tickets</p>
      </div>

      <div className="file-upload-container">
        <div
          className={`file-upload-area ${isDragging ? 'dragging' : ''} ${selectedFile ? 'has-file' : ''}`}
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          onClick={openFileDialog}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept={supportedFormats.join(',')}
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />

          {selectedFile ? (
            <div className="selected-file">
              <File className="file-icon" />
              <div className="file-info">
                <span className="file-name">{selectedFile.name}</span>
                <span className="file-size">
                  {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                </span>
              </div>
              <button
                type="button"
                className="remove-file-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  clearSelection();
                }}
              >
                <X />
              </button>
            </div>
          ) : (
            <div className="upload-placeholder">
              <Upload className="upload-icon" />
              <p className="upload-text">
                <strong>Click to browse</strong> or drag and drop files here
              </p>
              <p className="upload-subtext">
                Supported formats: PDF, DOC, DOCX, TXT (max 10MB)
              </p>
            </div>
          )}
        </div>

        {selectedFile && (
          <div className="upload-actions">
            <button
              type="button"
              className="upload-btn"
              onClick={uploadFile}
              disabled={isUploading}
            >
              {isUploading ? (
                <>
                  <div className="spinner"></div>
                  Uploading & Classifying...
                </>
              ) : (
                <>
                  <Upload />
                  Upload & Classify
                </>
              )}
            </button>
            <button
              type="button"
              className="cancel-btn"
              onClick={clearSelection}
              disabled={isUploading}
            >
              Cancel
            </button>
          </div>
        )}

        {uploadResult && (
          <div className={`upload-result ${uploadResult.success ? 'success' : 'error'}`}>
            {uploadResult.success ? (
              <>
                <CheckCircle className="result-icon" />
                <span>{uploadResult.message}</span>
              </>
            ) : (
              <>
                <AlertCircle className="result-icon" />
                <span>{uploadResult.message}</span>
              </>
            )}
          </div>
        )}
      </div>

      <div className="upload-info">
        <h3>How it works:</h3>
        <ol>
          <li><strong>Upload</strong> your support document (PDF, DOC, DOCX, TXT)</li>
          <li><strong>Parse</strong> the document content automatically</li>
          <li><strong>Classify</strong> using Llama 3.1 8B AI model</li>
          <li><strong>View</strong> the results in the dashboard below</li>
        </ol>
        <div className="supported-formats">
          <strong>Supported formats:</strong>
          <ul>
            <li>📄 PDF documents</li>
            <li>📝 Word documents (DOC, DOCX)</li>
            <li>📋 Text files (TXT)</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default FileUpload;
