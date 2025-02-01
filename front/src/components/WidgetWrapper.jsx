import React from 'react';

const WidgetWrapper = () => {
  return (
    <div className="widget-wrapper" style={{
      border: '2px solid #007bff',
      padding: '20px',
      borderRadius: '10px',
      marginTop: '40px'
    }}>
      <h2>Widget Preview</h2>
      <p>This widget can be embedded in your website. Copy the code below and add it to your site.</p>
      <pre style={{ background: '#f8f9fa', padding: '10px', textAlign: 'left' }}>
        {`<div id="ixtampa-widget"></div>
<script src="https://your-cdn.com/ixtampa-widget.bundle.js"></script>`}
      </pre>
    </div>
  );
};

export default WidgetWrapper;