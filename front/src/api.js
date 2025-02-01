import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:5000'; // Altere para a URL do seu backend se necessário

export const uploadImage = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
  return response.data; // espera { url: "..." }
};

export const generatePreview = async (imageUrl, clothingTemplate) => {
  const response = await axios.post(`${API_BASE_URL}/preview`, {
    image_url: imageUrl,
    clothing_template: clothingTemplate
  });
  return response.data; // espera { preview_url: "..." }
};