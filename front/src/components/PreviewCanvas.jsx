import React from 'react';

const PreviewCanvas = ({ previewUrl }) => {
  return (
    <div>
      <h2>Preview</h2>
      <img src={previewUrl} alt="Preview" style={{ maxWidth: '100%' }} />
    </div>
  );
};

export default PreviewCanvas;