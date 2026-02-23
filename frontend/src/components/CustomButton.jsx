// src/components/CustomButton.jsx
import React from 'react';
import styled from 'styled-components';

const CustomButton = ({ type = "button", children }) => {
  return (
    <StyledWrapper>
      <button className="btn" type={type}>
        {children}
      </button>
    </StyledWrapper>
  );
}

const StyledWrapper = styled.div`
  .btn {
    width: 100%;
    height: 50px;
    background: rgba(255, 255, 255, 0.15); /* خلفية شفافة */
    backdrop-filter: blur(10px); /* تأثير الزجاج */
    -webkit-backdrop-filter: blur(10px);
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.3); /* حدود شفافة */
    border-radius: 12px;
    font-size: 18px;
    font-weight: bold;
    font-family: 'Cairo', sans-serif;
    cursor: pointer;
    position: relative;
    z-index: 1;
    overflow: hidden;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1); /* ظل خفيف */
  }

  .btn:hover {
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
    border-color: rgba(255, 255, 255, 0.5);
  }

  /* تأثير الـ Shine عند اللمس */
  .btn:after {
    content: "";
    background: linear-gradient(120deg, transparent, rgba(255, 255, 255, 0.4), transparent); /* شعاع ضوئي */
    position: absolute;
    z-index: -1;
    left: -100%; /* يبدأ من بره */
    top: 0;
    bottom: 0;
    width: 100%;
    transform: skewX(-20deg); /* ميلان بسيط للشعاع */
    transition: 0.6s;
  }

  .btn:hover:after {
    left: 100%; /* يتحرك للناحية التانية */
  }
`;

export default CustomButton;