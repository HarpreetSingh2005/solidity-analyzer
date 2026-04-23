// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function balanceOf(address account) external view returns (uint256);
}

contract VulnAMMReserveManip {
    IERC20 public tokenA;
    IERC20 public tokenB;
    address public pool;

    // Vulnerability: Price derived from raw balance manipulation
    function getSpotPrice() public view returns (uint256) {
        uint256 resA = tokenA.balanceOf(pool);
        uint256 resB = tokenB.balanceOf(pool);
        return (resB * 1e18) / resA;
    }
}