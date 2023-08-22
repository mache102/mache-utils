const grayScaleShade0 = '#111';
const grayScaleShade1 = '#333';
const grayScaleShade2 = '#555';
const grayScaleShade3 = '#777';
const grayScaleShade4 = '#999';
const grayScaleShade5 = '#bbb';
const grayScaleShade6 = '#ddd';

const buttonSize = '50px'; /* Change the size of the button here */
const buttonOffset = '50px';
const buttonOpacity = 0.3; /* Change the default opacity of the button here */
const svgIconSize = '60%'; /* Change the size of the SVG icon here */

const svgIcon = `
<svg xmlns="http:/*www.w3.org/2000/svg" viewBox="0 0 512 512">
    <path d="M0 64C0 28.65 28.65 0 64 0H352C387.3 0 416 28.65 416 64V128C416 163.3 387.3 192 352 192H64C28.65 192 0 163.3 0 128V64zM160 352C160 334.3 174.3 320 192 320V304C192 259.8 227.8 224 272 224H416C433.7 224 448 209.7 448 192V69.46C485.3 82.64 512 118.2 512 160V192C512 245 469 288 416 288H272C263.2 288 256 295.2 256 304V320C273.7 320 288 334.3 288 352V480C288 497.7 273.7 512 256 512H192C174.3 512 160 497.7 160 480V352z"/>
</svg>`;

const rgb2hex = (rgb) => `#${rgb.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/).slice(1).map(n => parseInt(n, 10).toString(16).padStart(2, '0')).join('')}`;

function addColorModifier(parent, colorClass, labelText) {
    const listItem = document.createElement('div');
    listItem.classList.add('popup-list-item');
    listItem.style.display = 'flex';
    listItem.style.alignItems = 'center';
    listItem.style.margin = '20px 5px';
    listItem.style.fontWeight = 'bold';

    const label = document.createElement('div');
    label.style.color = grayScaleShade1;
    label.style.fontSize = '1rem';
    label.style.fontWeight = 'bold';
    label.style.marginRight = '10px';
    label.style.width = '100%';

    const classColorSpan = document.createElement('span');
    classColorSpan.textContent = colorClass;
    classColorSpan.style.color = 'black';
    label.appendChild(classColorSpan);

    const tabSpan = document.createElement('span');
    tabSpan.textContent = '\t\t';
    label.appendChild(tabSpan);

    const labelTextSpan = document.createElement('span');
    labelTextSpan.textContent = labelText;
    labelTextSpan.style.color = grayScaleShade4;
    labelTextSpan.style.fontSize = '0.9rem';
    labelTextSpan.style.fontStyle = 'italic';
    label.appendChild(labelTextSpan);

    /* add a color picker */
    const colorPicker = document.createElement('input');
    colorPicker.type = 'color';
    colorPicker.classList.add('color-picker');
    colorPicker.style.marginRight = '10px';
    colorPicker.style.width = '30px';
    colorPicker.style.height = '30px';
    colorPicker.style.borderRadius = '5px';
    colorPicker.style.border = 'none';
    colorPicker.style.outline = 'none';
    colorPicker.style.cursor = 'pointer';
    colorPicker.addEventListener('input', () => {
        colorInput.value = colorPicker.value;
    });

    /* Create an input for displaying the hex color value */
    const colorInput = document.createElement('input');
    colorInput.type = 'text';
    colorInput.classList.add('color-input');
    colorInput.style.width = '70px';
    colorInput.style.height = '20px';
    colorInput.style.borderRadius = '5px';
    colorInput.style.border = `1px solid ${grayScaleShade1}`;
    colorInput.style.color = grayScaleShade1;
    colorInput.style.fontWeight = 'bold';
    colorInput.maxLength = 7;
    colorInput.style.marginRight = '10px';
    colorInput.style.backgroundColor = 'white';
    colorInput.addEventListener('input', () => {
        if (/^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$/.test(colorInput.value)) {
            colorPicker.value = colorInput.value;
        }
    });

    /* Set the initial value of the color input 
     by getting the current color of the class (in hex) */
    const element = document.querySelector(`.${colorClass}`);
    const color = rgb2hex(window.getComputedStyle(element).color);
    colorPicker.value = color;
    colorInput.value = color;

    /* Create an 'Apply' button */
    const applyButton = document.createElement('button');
    applyButton.textContent = 'Apply';
    applyButton.classList.add('apply-button');
    applyButton.style.padding = '5px 10px';
    applyButton.style.backgroundColor = grayScaleShade1;
    applyButton.style.color = 'white';
    applyButton.style.fontWeight = 'bold';
    applyButton.style.border = 'none';
    applyButton.style.borderRadius = '5px';
    applyButton.style.cursor = 'pointer';

    applyButton.addEventListener('click', () => {
        /* Create or modify a <style> element to update the class color*/
        let styleElement = document.getElementById(`${colorClass}-style`);
    
        if (!styleElement) {
            styleElement = document.createElement('style');
            styleElement.id = `${colorClass}-style`;
            document.head.appendChild(styleElement);
        }
    
        styleElement.innerHTML = `.${colorClass} { color: ${colorPicker.value}; }`;
    
        console.log(`Updated color of ${colorClass} to ${colorPicker.value}`);
    });
 
    listItem.appendChild(label);
    listItem.appendChild(colorPicker);
    listItem.appendChild(colorInput);
    listItem.appendChild(applyButton);

    parent.appendChild(listItem);
}    

function showPopup() {
    const popupContainer = document.createElement('div');
    popupContainer.classList.add('popup-container');
    popupContainer.style.position = 'fixed';
    popupContainer.style.top = '0';
    popupContainer.style.left = '0';
    popupContainer.style.width = '100%';
    popupContainer.style.height = '100%';
    popupContainer.style.backgroundColor = 'rgba(0, 0, 0, 0.4)';
    popupContainer.style.display = 'flex';
    popupContainer.style.alignItems = 'center';
    popupContainer.style.justifyContent = 'center';
    popupContainer.style.zIndex = '1000';
    
    const popup = document.createElement('div');
    popup.classList.add('popup');
    popup.style.position = 'fixed';
    popup.style.backgroundColor = 'white';
    popup.style.padding = '20px';
    popup.style.width = '600px';
    popup.style.borderRadius = '5px';
    popup.style.boxShadow = '0px 2px 4px rgba(0, 0, 0, 0.2)';
    
    const popupHeader = document.createElement('div');
    popupHeader.textContent = 'Edit Theme Colors';
    popupHeader.classList.add('popup-header');
    popupHeader.style.position = 'absolute';
    popupHeader.style.top = '10px';
    popupHeader.style.left = '20px';
    popupHeader.style.fontSize = '1.2rem';
    popupHeader.style.fontWeight = 'bold';
    popupHeader.style.textDecoration = 'underline';
    popupHeader.style.color = grayScaleShade1;
    popupHeader.style.marginBottom = '10px';

    const popupCloseButton = document.createElement('div');
    popupCloseButton.textContent = '×';
    popupCloseButton.classList.add('popup-close');
    popupCloseButton.style.position = 'absolute';
    popupCloseButton.style.top = '3px';
    popupCloseButton.style.right = '10px';
    popupCloseButton.style.cursor = 'pointer';
    popupCloseButton.style.color = grayScaleShade1;
    popupCloseButton.style.fontSize = '1.5rem';
    
    

    popupCloseButton.addEventListener('click', () => {
        document.body.removeChild(popupContainer);
    });
    
    popup.appendChild(popupCloseButton);
    popup.appendChild(popupHeader);
    /* Append your list items to the popup*/
    
    addColorModifier(popup, "mtk1", "variable names")
    addColorModifier(popup, "mtk3", "functions & classes")
    addColorModifier(popup, "mtk4", "parameters")
    addColorModifier(popup, "mtk5", "standard comments (#)")
    addColorModifier(popup, "mtk6", "numbers")
    addColorModifier(popup, "mtk8", "class \"self\"")
    addColorModifier(popup, "mtk9", "keywords (if, else,...)")
    addColorModifier(popup, "mtk10", "single & double quotes (', \")")
    addColorModifier(popup, "mtk11", "equals, double equals (=, ==)")
    addColorModifier(popup, "mtk13", "strings (including triple quotes)")

    popupContainer.appendChild(popup);
    document.body.appendChild(popupContainer);
}
  
function addCircularButton() {
    const button = document.createElement('div');
    button.classList.add('mc-theme-editor-btn'); /* Add the class "mc-theme-editor-btn"*/
    button.style.position = 'fixed';
    button.style.bottom = buttonOffset;
    button.style.right = buttonOffset;
    button.style.width = buttonSize;
    button.style.height = buttonSize;
    button.style.backgroundColor = `rgba(255, 255, 255, ${buttonOpacity})`;
    button.style.borderRadius = '50%';
    button.style.boxShadow = '0px 2px 4px rgba(0, 0, 0, 0.2)';
    button.style.display = 'flex';
    button.style.justifyContent = 'center';
    button.style.alignItems = 'center';
    button.style.cursor = 'pointer';
    button.style.transition = 'background-color 0.15s';
    
    const iconWrapper = document.createElement('div');
    iconWrapper.style.width = svgIconSize;
    iconWrapper.style.height = svgIconSize;
    iconWrapper.innerHTML = svgIcon;
    button.appendChild(iconWrapper);

    /* Modify the click event to open the popup*/
    button.addEventListener('click', () => {
        showPopup();
    });

    /* Add the mouseenter and mouseleave event listeners*/
    button.addEventListener('mouseenter', () => {
        button.style.backgroundColor = `rgba(255, 255, 255, 0.8)`;
    });

    button.addEventListener('mouseleave', () => {
        button.style.backgroundColor = `rgba(255, 255, 255, ${buttonOpacity})`;
    });

    document.body.appendChild(button);
}

/* Call the function to add the circular button to the webpage*/
addCircularButton();
