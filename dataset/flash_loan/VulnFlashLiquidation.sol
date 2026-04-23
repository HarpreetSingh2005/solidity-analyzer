// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnFlashLiquidation {
    mapping(address => uint256) public collaterals;
    
    function getSpotPrice() public view returns (uint256) {
        // Vulnerable spot price logic
        return address(this).balance; 
    }

    // Vulnerability: Flash loan can manipulate spot price to force liquidations
    function liquidate(address user) external {
        uint256 price = getSpotPrice();
        require(collaterals[user] * price < 1000, "Not liquidatable");
        collaterals[user] = 0; // Liquidated
    }
}