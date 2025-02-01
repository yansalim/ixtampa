import React, { useState } from 'react';
import { uploadImage } from '../api';

const ImageUploader = ({ onUpload }) => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    try {
      const response = await uploadImage(file);
      onUpload(response.url);
    } catch (error) {
      console.error("Error uploading image:", error);
    }
    setUploading(false);
  };

  return (
    <div>
      <h2>Upload Your Logo</h2>
      <input type="file" accept="image/*" onChange={handleFileChange} />
      <button onClick={handleUpload} disabled={uploading}>
        {uploading ? 'Uploading...' : 'Upload'}
      </button>
    </div>
  );
};

export default ImageUploader;