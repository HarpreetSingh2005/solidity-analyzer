// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnFlashMintExcess {
    uint256 public totalLPTokens;

    // Vulnerability: Mints LP tokens based on spot balance, which can be inflated by flash loans
    function deposit() external payable {
        uint256 amountToMint = msg.value * totalLPTokens / address(this).balance;
        totalLPTokens += amountToMint;
    }
}