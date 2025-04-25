class MyDashboardPanel extends HTMLElement {
    set hass(hass) {
        this.innerHTML = `
            <h1>Můj vlastní dashboard</h1>
            <p>Napojený na Home Assistant</p>
        `;
    }
}

customElements.define('licon-panel', MyDashboardPanel);