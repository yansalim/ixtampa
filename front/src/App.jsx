import React, { useState } from 'react';
import ClothingSelector from './components/ClothingSelector';
import ImageUploader from './components/ImageUploader';
import PreviewCanvas from './components/PreviewCanvas';
import WidgetWrapper from './components/WidgetWrapper';
import { generatePreview } from './api';

function App() {
  const [selectedClothing, setSelectedClothing] = useState(null);
  const [uploadedImage, setUploadedImage] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);

  const handleGeneratePreview = async () => {
    if (!uploadedImage || !selectedClothing) {
      alert("Selecione uma peça e faça o upload da sua logo!");
      return;
    }
    try {
      // Chama o backend para gerar o preview
      const response = await generatePreview(uploadedImage, selectedClothing.template);
      setPreviewUrl(response.preview_url);
    } catch (error) {
      console.error("Erro ao gerar preview:", error);
    }
  };

  return (
    <div className="app-container">
      <h1>Ixtampa Customization</h1>
      <ClothingSelector onSelect={setSelectedClothing} />
      <ImageUploader onUpload={setUploadedImage} />
      <button onClick={handleGeneratePreview}>
        Generate Preview
      </button>
      {previewUrl && <PreviewCanvas previewUrl={previewUrl} />}
      <hr />
      <WidgetWrapper />
    </div>
  );
}

export default App;