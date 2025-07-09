// Simple test JavaScript file
console.log('Simple app.js loaded successfully');

// Simple function to test
function simpleTest() {
    console.log('simpleTest function called');
    const container = document.getElementById('event-cards-container');
    console.log('Container in simpleTest:', container);
    
    if (container) {
        console.log('Setting container innerHTML...');
        container.innerHTML = `
            <div style="background: rgba(0, 0, 0, 0.6); border: 1px solid #00ffff; border-radius: 8px; padding: 20px; margin: 10px 0;">
                <h3>🎉 Simple Test Success!</h3>
                <p>This proves JavaScript is working</p>
                <p>Date: ${new Date().toLocaleDateString()}</p>
                <p>Time: ${new Date().toLocaleTimeString()}</p>
            </div>
        `;
        console.log('Container innerHTML set successfully');
        
        // Hide test message
        const testMessage = document.querySelector('.test-message');
        if (testMessage) {
            console.log('Hiding test message...');
            testMessage.style.display = 'none';
        }
    } else {
        console.error('Container not found in simpleTest!');
    }
}

// DOM Content Loaded event
document.addEventListener('DOMContentLoaded', () => {
    console.log('Simple app: DOM Content Loaded');
    
    // Add simple test to global scope
    window.simpleTest = simpleTest;
    
    // Check if container exists
    const container = document.getElementById('event-cards-container');
    console.log('Container found:', !!container);
    
    // Auto-run the test
    setTimeout(() => {
        console.log('Auto-running simple test...');
        try {
            simpleTest();
            console.log('Simple test completed successfully');
        } catch (error) {
            console.error('Error in simple test:', error);
        }
    }, 2000); // Increased to 2 seconds
});