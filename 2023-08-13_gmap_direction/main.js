// Initialize a FIFO queue to store coordinates
const coordinateQueue = [];

// Function to calculate the direction between two points in degrees
function calculateDirection(lat1, lon1, lat2, lon2) {
    const y = Math.sin(lon2 - lon1) * Math.cos(lat2);
    const x = Math.cos(lat1) * Math.sin(lat2) - Math.sin(lat1) * Math.cos(lat2) * Math.cos(lon2 - lon1);
    const angle = Math.atan2(y, x);
    const degrees = (angle * 180) / Math.PI;
    return (degrees + 360) % 360;
}

// Function to update the coordinates and calculate the direction
function updateCoordinates() {
    const button = document.querySelector('.ZqLNQd.t9f27');
    if (button) {
        const text = button.textContent.trim();
        const [lat, lon] = text.split(', ');

        const newCoordinate = { lat: parseFloat(lat), lon: parseFloat(lon) };

        if (coordinateQueue.length < 2) {
            coordinateQueue.push(newCoordinate);
        } else {
            const coordinate1 = coordinateQueue.shift();
            const coordinate2 = coordinateQueue[0];
            coordinateQueue.push(newCoordinate);

            const direction = calculateDirection(
                coordinate1.lat,
                coordinate1.lon,
                coordinate2.lat,
                coordinate2.lon
            );

            console.log(`Direction: ${direction.toFixed(2)} degrees`);
        }
        
        console.log('Coordinates:', coordinateQueue);
    }
}

// Set up a mutation observer to watch for changes in the button's text
const targetNode = document.querySelector('.ZqLNQd.t9f27');
const config = { characterData: true, subtree: true };
const observer = new MutationObserver(updateCoordinates);
observer.observe(targetNode, config);

// Initial call to updateCoordinates
updateCoordinates();
