// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
interface IERC20 { function balanceOf(address) external view returns (uint256); }
// Vulnerability: Price derived from raw balance.
contract VulnNewOracleSpot2 {
    IERC20 public token;
    function getPrice() public view returns (uint256) {
        return token.balanceOf(address(this)); // Easily manipulated via direct transfer
    }
}