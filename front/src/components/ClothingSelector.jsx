import React from 'react';

const ClothingSelector = ({ onSelect }) => {
  // Exemplos de peças; cada item tem um id, nome e caminho do template (logo)
  const clothingOptions = [
    { id: 'tshirt', name: 'T-Shirt', template: '/templates/tshirt.png' },
    { id: 'hoodie', name: 'Hoodie', template: '/templates/hoodie.png' }
  ];

  const handleChange = (event) => {
    const selected = clothingOptions.find(item => item.id === event.target.value);
    onSelect(selected);
  };

  return (
    <div>
      <h2>Select Clothing</h2>
      <select onChange={handleChange} defaultValue="">
        <option value="" disabled>Select an option</option>
        {clothingOptions.map(option => (
          <option key={option.id} value={option.id}>
            {option.name}
          </option>
        ))}
      </select>
    </div>
  );
};

export default ClothingSelector;