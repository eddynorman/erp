document.addEventListener("DOMContentLoaded", function () {
    // Get elements
    const assetDetail = document.getElementById("asset-details");
    const assetDetailButton = document.getElementById("asset-details-button");
    const assetHistory = document.getElementById("asset-history");
    const assetHistoryButton = document.getElementById("asset-history-button");
    const historyButtons = document.querySelectorAll(".asset-history-button");

    const purchaseHistory = document.getElementById("purchase-history");
    const damageHistory = document.getElementById("damage-history");
    const repairHistory = document.getElementById("repair-history");
    const disposalHistory = document.getElementById("disposal-history");

    const purchaseHistoryButton = document.getElementById("purchase-history-button");
    const damageHistoryButton = document.getElementById("damage-history-button");
    const repairHistoryButton = document.getElementById("repair-history-button");
    const disposalHistoryButton = document.getElementById("disposal-history-button");

    // Initial state
    assetDetail.style.display = "block";
    assetHistory.style.display = "none";
    historyButtons.forEach(button => button.style.display = "none");

    // Function to hide all history sections
    function hideAllHistorySections() {
        purchaseHistory.style.display = "none";
        damageHistory.style.display = "none";
        repairHistory.style.display = "none";
        disposalHistory.style.display = "none";
    }

    // Event listener for "Asset Details" button
    assetDetailButton.addEventListener("click", function () {
        assetDetail.style.display = "block";
        assetHistory.style.display = "none";
        historyButtons.forEach(button => button.style.display = "none");
    });

    // Event listener for "Asset History" button
    assetHistoryButton.addEventListener("click", function () {
        assetDetail.style.display = "none";
        assetHistory.style.display = "block";
        historyButtons.forEach(button => button.style.display = "inline-block");

        hideAllHistorySections();
        purchaseHistory.style.display = "block"; // Show the first history by default
    });

    // Event listeners for history buttons
    purchaseHistoryButton.addEventListener("click", function () {
        hideAllHistorySections();
        purchaseHistory.style.display = "block";
    });

    damageHistoryButton.addEventListener("click", function () {
        hideAllHistorySections();
        damageHistory.style.display = "block";
    });

    repairHistoryButton.addEventListener("click", function () {
        hideAllHistorySections();
        repairHistory.style.display = "block";
    });

    disposalHistoryButton.addEventListener("click", function () {
        hideAllHistorySections();
        disposalHistory.style.display = "block";
    });
});
