// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnFlashArbitrage {
    uint256 public reserveA = 1000;
    uint256 public reserveB = 1000;

    // Vulnerability: Simple constant product AMM with no slippage protection
    function swapAToB(uint256 amountA) external {
        uint256 amountOut = (amountA * reserveB) / (reserveA + amountA);
        reserveA += amountA;
        reserveB -= amountOut;
        // Transfer B to sender
    }
}