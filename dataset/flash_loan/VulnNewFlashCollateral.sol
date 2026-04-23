// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Collateral value inflated by flash loan to borrow unbacked assets.
contract VulnNewFlashCollateral {
    function borrow(uint256 amount) external {
        uint256 collateralValue = address(this).balance; // Flash loanable
        require(amount <= collateralValue / 2, "Overborrow");
    }
}